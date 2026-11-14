"""Portuguese prompts are classified like English ones, and a short order is a task.

The keyword rules only knew English. A Portuguese request fell back to
``general`` unless it happened to contain an English term such as "pull request"
or "deploy". And any prompt under four words was treated as a follow-up, so
"Corrija o bug" or "Run the tests" got the few-lines context instead of the task's
profile.
"""

from __future__ import annotations

from collections import Counter
from pathlib import Path

import pytest
from test_hook_policies import NOW, event, policy_config

from briefspec.hooks import process_event
from briefspec.models import Runtime, WorkType
from briefspec.state import load_session
from briefspec.work_types import classify_task, is_clear_pivot, is_order, is_substantive


def _corpus() -> list[tuple[str, str]]:
    templates = {
        "general": "Qual é o significado do termo comum {index} em uma frase?",
        "exploration": "Explore o repositório {index} e mapeie os pontos de entrada e o fluxo.",
        "review": "Revise o pull request #{index} e audite o risco de merge.",
        "implementation": "Implemente a funcionalidade {index} e adicione testes para ela.",
        "debugging": "Depure o teste {index} que está falhando e ache a causa raiz.",
        "planning": "Planeje as fases e os critérios de aceite da funcionalidade {index}.",
        "research": "Pesquise as mudanças recentes do mercado para a ferramenta {index}.",
        "operations": "Trate o incidente {index} em produção: monitore e faça o rollback.",
    }
    return [
        (work_type, template.format(index=index))
        for work_type, template in templates.items()
        for index in range(1, 21)
    ]


def test_portuguese_corpus_matches_the_declared_vocabulary() -> None:
    corpus = _corpus()
    expected = [work_type for work_type, _ in corpus]
    actual = [classify_task(prompt).work_type for _, prompt in corpus]
    assert Counter(expected) == Counter({work_type.value: 20 for work_type in WorkType})
    wrong = [
        (want, got, prompt)
        for (want, prompt), got in zip(corpus, actual, strict=True)
        if want != got
    ]
    assert wrong == []


@pytest.mark.parametrize(
    ("prompt", "expected"),
    [
        (
            "Você é o revisor independente de uma entrega feita por outro agente. "
            "Aponte cada achado com a prova.",
            "review",
        ),
        ("Revise esta entrega e diga se posso aprovar.", "review"),
        ("Faça uma auditoria desta mudança antes do merge.", "review"),
        ("Corrija o bug de login que quebra quando a senha tem acento.", "implementation"),
        ("Implemente a tela de cadastro de clientes com validação de CPF.", "implementation"),
        ("Atualize a biblioteca de datas e ajuste as chamadas.", "implementation"),
        ("Planeje a migração do banco para a nova versão.", "planning"),
        ("Investigue por que o teste de integração falha no Windows.", "debugging"),
        ("Por que o login trava depois do segundo acesso?", "debugging"),
        ("Pesquise as opções de fila de mensagens e compare custo e latência.", "research"),
        ("Faça o deploy da versão nova e confira os logs.", "operations"),
        ("Onde fica a regra de desconto e como funciona o cálculo?", "exploration"),
        # Without accents, as people type on a keyboard that lacks them.
        ("Faca a revisao de codigo desta alteracao.", "review"),
        ("Planeje a implantacao com fases e criterios de aceite.", "planning"),
    ],
)
def test_portuguese_requests_get_the_right_work_type(prompt: str, expected: str) -> None:
    result = classify_task(prompt)
    assert (result.work_type, result.origin, result.confidence) == (expected, "inferred", "medium")


@pytest.mark.parametrize(
    ("prompt", "expected_type", "expected_subject"),
    [
        ("Revise o pull request 42 e aponte o risco.", "review", "pull-request"),
        ("Corrija o defeito no cálculo de frete.", "implementation", "bug"),
        ("Revise a segurança da autenticação.", "review", "security"),
        ("Atualize a documentação da instalação.", "implementation", "document"),
        ("Implemente a migração da tabela de pedidos.", "implementation", "data"),
    ],
)
def test_portuguese_subjects_are_recognized(
    prompt: str, expected_type: str, expected_subject: str
) -> None:
    result = classify_task(prompt)
    assert (result.work_type, result.subject) == (expected_type, expected_subject)


@pytest.mark.parametrize(
    ("prompt", "expected"),
    [
        ("Não implemente nada; apenas revise o pull request 7.", "review"),
        ("Nao implemente nada; apenas revise o pull request 7.", "review"),
        ("Sem alterar o código, explore o repositório e mapeie o fluxo.", "exploration"),
        ("Nunca publique sem aviso. Corrija o teste que está vermelho.", "implementation"),
    ],
)
def test_portuguese_negations_do_not_drive_the_type(prompt: str, expected: str) -> None:
    assert classify_task(prompt).work_type == expected


@pytest.mark.parametrize(
    "prompt",
    [
        "Oi, tudo bem com você hoje?",
        "Obrigado, ficou bom assim mesmo.",
        "O projeto da empresa tem três pessoas.",
        "Use quebras de linha LF no arquivo de texto.",
        "Qual é a capital do Brasil e quantos habitantes tem?",
    ],
)
def test_ordinary_portuguese_sentences_stay_general(prompt: str) -> None:
    result = classify_task(prompt)
    assert (result.work_type, result.origin) == ("general", "fallback")


def test_portuguese_pivot_is_recognized() -> None:
    assert is_clear_pivot("Nova tarefa: revise o pull request 9.")
    assert is_clear_pivot("Agora revise o que foi feito no módulo de pagamento.")
    assert is_clear_pivot("Em vez disso, planeje a migração.")
    assert not is_clear_pivot("Continue de onde parou, por favor.")


@pytest.mark.parametrize(
    "prompt",
    [
        "Corrija o bug",
        "Rode os testes",
        "Por favor, rode os testes",
        "Faça o deploy",
        "Revise o PR",
        "Run the tests",
        "Fix it",
        "Please fix it",
        "Deploy now",
    ],
)
def test_a_short_order_is_a_task(prompt: str) -> None:
    assert is_order(prompt)
    assert is_substantive(prompt)


@pytest.mark.parametrize(
    "prompt",
    [
        "",
        "ok",
        "continue",
        "Continue",
        "Merge feito",
        "Como estamos?",
        "Pode aplicar",
        "Obrigado",
        "sim",
        "Tem alguma previsão?",
        "Looks good",
        "yes please",
    ],
)
def test_a_short_reply_is_not_an_order(prompt: str) -> None:
    assert not is_order(prompt)
    assert not is_substantive(prompt)


def test_short_order_gets_the_full_profile_and_short_reply_stays_short(
    isolated_homes: dict[str, Path],
) -> None:
    first, first_payload = event(
        Runtime.CLAUDE,
        "UserPromptSubmit",
        "short-order",
        prompt="Revise o pull request 42 e aponte o risco de merge.",
    )
    assert "Use the brief-spec skill" in (
        process_event(first, first_payload, policy_config()).context or ""
    )
    assert load_session(Runtime.CLAUDE, "short-order", NOW).work_type == "review"
    for text in ("Corrija o bug", "Rode os testes", "Run the tests"):
        later, later_payload = event(Runtime.CLAUDE, "UserPromptSubmit", "short-order", prompt=text)
        context = process_event(later, later_payload, policy_config()).context or ""
        assert "Use the brief-spec skill" in context, text
        assert "short follow-up" not in context, text
    for text in ("Merge feito", "continue", "Como estamos?"):
        later, later_payload = event(Runtime.CLAUDE, "UserPromptSubmit", "short-order", prompt=text)
        context = process_event(later, later_payload, policy_config()).context or ""
        assert "short follow-up" in context, text


def test_a_session_that_opens_with_a_short_order_is_classified(
    isolated_homes: dict[str, Path],
) -> None:
    first, first_payload = event(
        Runtime.CLAUDE, "UserPromptSubmit", "opens-short", prompt="Corrija o bug"
    )
    context = process_event(first, first_payload, policy_config()).context or ""
    assert "Use the brief-spec skill" in context
    assert load_session(Runtime.CLAUDE, "opens-short", NOW).work_type == "implementation"
