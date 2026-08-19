---
name: intelligent-debug-logging
description: >
  Instrumenta qualquer processo com logs padronizados e inteligentes para debug de qualidade.
  Triggers include 'debug [processo]', 'instrumentar logs em [feature]', 'adicionar prints em [fluxo]',
  'rastrear [operação]', 'log inteligente para [módulo]'.
  Use quando o usuário quiser acompanhar como um recurso funciona por baixo dos panos.
version: 1.0.0
tags: [debug, logging, observability, agnostic, dart, flutter]
difficulty: intermediate
estimated_time: 10-15min
---

# 🚀 Intelligent Debug Logging

Central de log inteligente para acompanhar como qualquer recurso funciona por baixo dos panos.
Normatiza prints para que todo debug tenha qualidade, rastreabilidade e fácil visualização.

## When to use this skill

- Quando o usuário pedir: "debug [processo]", "rastrear [fluxo]", "instrumentar [módulo]"
- Quando precisar testar fluxos de sincronização local ↔ remoto
- Quando quiser confirmar resultado de cálculos complexos
- Quando precisar validar caminho feliz vs caminho triste de uma operação
- Quando quiser rastrear chamadas de API (request/response)
- Quando investigar um bug e precisar de visibilidade do fluxo interno
- Quando quiser medir performance de operações críticas

## Prerequisites

- Acesso ao código-fonte do processo a ser instrumentado
- Conhecimento da arquitetura do módulo alvo (classes, métodos, fluxo)

## Workflow

- [ ] **Passo 1 — Identificar**: Usuário escolhe o processo/recurso a instrumentar
- [ ] **Passo 2 — Mapear**: Levantar classes e métodos envolvidos no fluxo
- [ ] **Passo 3 — Gerar**: Criar prints padronizados seguindo as regras abaixo
- [ ] **Passo 4 — Entregar**: Apresentar tabela de debug points + sequência esperada de logs

---

## Instructions

### 📦 Imports Necessários

Para utilizar `debugPrint` e `jsonEncode`, certifique-se de incluir no topo do arquivo:

```dart
import 'package:flutter/foundation.dart'; // Para debugPrint
import 'dart:convert'; // Para jsonEncode (opcional, para logs complexos)
```

### 🔑 Regra de Ouro do Print

Todo `debugPrint` DEVE conter **3 partes obrigatórias**:

```
EMOJI [Classe.método] <nome_resultado> valor
```

| Parte                  | Descrição                               | Exemplo                 |
| ---------------------- | --------------------------------------- | ----------------------- |
| **EMOJI**              | Indica o tipo da operação (ver legenda) | `🚀`                    |
| **[Classe.método]**    | Onde o print acontece                   | `[SyncManager.runSync]` |
| **\<nome_resultado\>** | Label do que está sendo logado          | `<userId>`              |
| **valor**              | O valor real da variável/resultado      | `abc123`                |

### 📋 Legenda de Emojis

| Emoji | Significado                 | Quando Usar                        |
| ----- | --------------------------- | ---------------------------------- |
| 🚀    | Início de operação          | Entry point de métodos importantes |
| ✅    | Sucesso (caminho feliz)     | Operação concluída com êxito       |
| ❌    | Erro (caminho triste)       | Catch de exceções, falhas          |
| 📥    | Download / Recebimento      | Dados chegando de fonte externa    |
| 📤    | Upload / Envio              | Dados sendo enviados para fora     |
| 💾    | Escrita local               | Cache, banco local, SharedPrefs    |
| 📊    | Resultado de cálculo        | Contagens, totais, métricas        |
| 🔄    | Operação em andamento       | Processos assíncronos, loops       |
| ⚠️    | Aviso / situação inesperada | Dados inesperados, fallbacks       |
| 🗑️    | Exclusão / Cleanup          | Deletes, limpeza de dados          |
| 🌐    | Chamada de API              | HTTP requests, respostas           |
| ⏱️    | Performance / Timing        | Medição de tempo de execução       |
| 👁️    | Stream / Watch ativado      | Listeners, observers, streams      |
| 💊    | Recuperação de dados        | Retry, fallback, recovery          |

---

### 🧱 Templates de Print por Tipo

#### Tipo 1: Valor Simples

```dart
debugPrint('🚀 [{{Classe}}.{{método}}] <{{label}}> ${{variável}}');
```

**Exemplo real:**

```dart
debugPrint('🚀 [SyncManager.runSync] <userId> $userId');
```

#### Tipo 2: Sucesso (Caminho Feliz)

```dart
debugPrint('✅ [{{Classe}}.{{método}}] <{{label}}> ${{variável}}');
```

**Exemplo real:**

```dart
debugPrint('✅ [PaymentService.processPayment] <transactionId> $txId');
```

#### Tipo 3: Erro (Caminho Triste)

```dart
debugPrint('❌ [{{Classe}}.{{método}}] <error> ${e.message}');
debugPrint('❌ [{{Classe}}.{{método}}] <stackTrace>\n$stackTrace');
```

**Exemplo real:**

```dart
try {
  await apiService.fetchData();
} catch (e, stackTrace) {
  debugPrint('❌ [ApiService.fetchData] <error> ${e.message}');
  debugPrint('❌ [ApiService.fetchData] <stackTrace>\n$stackTrace');
}
```

#### Tipo 4: JSON Formatado

Quando o valor é um Map ou JSON, **sempre formatar** para visualização legível:

```dart
import 'dart:convert';

debugPrint('📥 [{{Classe}}.{{método}}] <{{label}}>\n${const JsonEncoder.withIndent("  ").convert({{jsonMap}})}');
```

**Exemplo real:**

```dart
final responseBody = jsonDecode(response.body);
debugPrint('📥 [ApiService.fetchUser] <response_body>\n${const JsonEncoder.withIndent("  ").convert(responseBody)}');
```

**Saída esperada:**

```log
📥 [ApiService.fetchUser] <response_body>
{
  "id": "user-123",
  "name": "João",
  "email": "joao@email.com"
}
```

#### Tipo 5: Coleção / Contagem

```dart
debugPrint('📊 [{{Classe}}.{{método}}] <{{label}}_count> ${{{lista}}.length}');
```

**Exemplo real:**

```dart
debugPrint('📊 [SyncManager.download] <escalas_count> ${escalas.length}');
```

#### Tipo 6: Chamada de API

```dart
// Request
debugPrint('🌐 [{{Classe}}.{{método}}] <request> {{HTTP_METHOD}} $url');
debugPrint('🌐 [{{Classe}}.{{método}}] <request_body>\n${const JsonEncoder.withIndent("  ").convert(body)}');

// Response
debugPrint('🌐 [{{Classe}}.{{método}}] <response_status> ${response.statusCode}');
debugPrint('🌐 [{{Classe}}.{{método}}] <response_body>\n${const JsonEncoder.withIndent("  ").convert(jsonDecode(response.body))}');
```

#### Tipo 7: Performance / Timing

```dart
final stopwatch = Stopwatch()..start();
// ... operação ...
stopwatch.stop();
debugPrint('⏱️ [{{Classe}}.{{método}}] <elapsed_ms> ${stopwatch.elapsedMilliseconds}ms');
```

**Exemplo real:**

```dart
final sw = Stopwatch()..start();
final result = await heavyComputation();
sw.stop();
debugPrint('⏱️ [CalcService.computeSchedule] <elapsed_ms> ${sw.elapsedMilliseconds}ms');
debugPrint('📊 [CalcService.computeSchedule] <result_count> ${result.length}');
```

#### Tipo 8: Fluxo Completo (Entry → Exit)

Para métodos críticos, instrumentar **entrada e saída**:

```dart
Future<void> processOrder(String orderId) async {
  debugPrint('🚀 [OrderService.processOrder] <orderId> $orderId');
  try {
    final order = await fetchOrder(orderId);
    debugPrint('📥 [OrderService.processOrder] <order_status> ${order.status}');

    final result = await validateOrder(order);
    debugPrint('📊 [OrderService.processOrder] <validation_result> $result');

    await submitOrder(order);
    debugPrint('✅ [OrderService.processOrder] <orderId> $orderId');
  } catch (e) {
    debugPrint('❌ [OrderService.processOrder] <error> ${e.message}');
    rethrow;
  }
}
```

---

### 📐 Regras de Qualidade

1. **Nunca** usar `print()` — sempre `debugPrint()` (limita tamanho no console)
2. **Nunca** fazer print sem as 3 partes: `EMOJI [Classe.método] <label> valor`
3. **Sempre** formatar JSON com indentação de 2 espaços
4. **Sempre** incluir o `catch` com print de erro ao instrumentar um `try`
5. **Sempre** logar contagens de coleções, nunca a coleção inteira (exceto se < 5 items)
6. **Sempre** incluir `<label>` mesmo que o valor seja óbvio — facilita grep no console
7. Para listas grandes, logar apenas `.length` e os primeiros 3 items como amostra

---

## 🎯 Output Template

Ao instrumentar um processo, o agente DEVE entregar:

### Parte 1: Tabela de Debug Points

| #   | Classe       | Método       | Debug Message                                      |
| --- | ------------ | ------------ | -------------------------------------------------- |
| 1   | `{{Classe}}` | `{{método}}` | `🚀 [{{Classe}}.{{método}}] <{{label}}> {{valor}}` |
| 2   | ...          | ...          | ...                                                |

### Parte 2: Sequência Esperada de Logs

#### Caminho Feliz ✅

```log
🚀 [Classe.método] <label> valor_entrada
🔄 [Classe.método] <label> processando...
📊 [Classe.método] <label_count> 42
✅ [Classe.método] <label> valor_sucesso
```

#### Caminho Triste ❌

```log
🚀 [Classe.método] <label> valor_entrada
🔄 [Classe.método] <label> processando...
❌ [Classe.método] <error> mensagem_do_erro
```

### Parte 3: Arquivos Modificados

| Arquivo       | Linhas Aprox. | Responsabilidade |
| ------------- | ------------- | ---------------- |
| `{{arquivo}}` | {{linhas}}    | {{o que faz}}    |

---

## 🛠️ Como o Usuário Filtra no Console

Orientar o usuário a filtrar por emoji no console de debug:

- `🚀` → Ver apenas inícios de operação
- `📥` → Ver apenas downloads/recebimentos
- `📤` → Ver apenas uploads/envios
- `✅` → Ver apenas sucessos
- `❌` → Ver apenas erros
- `🌐` → Ver apenas chamadas de API
- `⏱️` → Ver apenas métricas de performance
- `[NomeDaClasse` → Ver apenas prints de uma classe específica

---

## Error Handling

### Problema: Print muito longo truncado no console

**Sintoma:** JSON ou stacktrace cortado no console do Flutter
**Causa:** `debugPrint` tem limite de ~800 chars por chamada
**Solução:** Quebrar em múltiplos prints:

```dart
final jsonStr = const JsonEncoder.withIndent("  ").convert(bigJson);
// Quebra em chunks de 800 chars
for (var i = 0; i < jsonStr.length; i += 800) {
  debugPrint(jsonStr.substring(i, (i + 800).clamp(0, jsonStr.length)));
}
```

### Problema: Prints aparecem fora de ordem

**Sintoma:** Sequência de logs não respeita a ordem do código
**Causa:** Operações assíncronas executam em paralelo
**Solução:** Adicionar timestamp nos prints críticos:

```dart
debugPrint('🚀 [${DateTime.now().toIso8601String()}] [Classe.método] <label> $valor');
```

### Problema: Print em produção

**Sintoma:** Logs aparecendo em release build
**Causa:** `debugPrint` é no-op em release por padrão, mas `print()` não
**Solução:** Sempre usar `debugPrint()` e nunca `print()`. Se necessário, usar `kDebugMode`:

```dart
if (kDebugMode) {
  debugPrint('🚀 [Classe.método] <label> $valor');
}
```

---

## Related Skills

- `investigating-bugs` — conduzir diagnóstico estruturado quando logs apontarem regressão de sincronização.

## Changelog

### v1.0.0 (2026-02-17)

- Initial release
- Padrão de log com 3 partes obrigatórias (emoji + método + label + valor)
- 14 emojis na legenda
- 8 templates de print (simples, sucesso, erro, JSON, coleção, API, timing, fluxo completo)
- Output template com tabela, sequência esperada e arquivos modificados
- Error handling para truncamento, ordem e produção
