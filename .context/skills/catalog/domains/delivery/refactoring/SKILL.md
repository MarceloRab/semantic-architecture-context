---
name: refactoring
description: Refatoração segura com verificação de não-regressão. Prioriza correção cirúrgica sobre mudanças arquiteturais.
version: 1.0.0
tags: [refactor, safety, minimal-change, dart, flutter, getx]
author: Tô de Plantão
urgency: high
scope: project-specific
---

# 🔧 Refactoring Skill

Um agente de refatoração que prioriza **segurança sobre elegância**. Aplica o princípio da **Correção Cirúrgica**: a menor mudança possível que resolve o problema.

---

## 🎯 **Princípios Core**

### 1. **Correção Mínima Primeiro**

> "Não refatore o motor quando só precisa trocar a vela."

- ✅ **Correção Cirúrgica**: 1-5 linhas que resolvem o problema
- ⚠️ **Refatoração Moderada**: Extração de método, renomeação
- ❌ **Reescrita Arquitetural**: Apenas se absolutamente necessário

### 2. **Funcionalidade Invariante**

```
ANTES da refatoração: Sistema faz X
DEPOIS da refatoração: Sistema AINDA faz X (exatamente igual)
```

- **Nunca** alterar output ou side effects
- **Nunca** introduzir features durante refatoração
- Refatoração é **puramente estrutural**

### 3. **Reversibilidade**

- Mudanças devem ser **facilmente reversíveis** via git
- Preferir commits pequenos e atômicos
- Se em dúvida, **não refatore**

---

## 🧠 **Protocolo de Refatoração**

### **Step 1: Diagnóstico**

**Antes de qualquer mudança:**

1. **Identifique o problema exato**

   ```
   ❌ "O código está confuso" (vago)
   ✅ "fireImmediately:true dispara antes do sync completar" (específico)
   ```

2. **Documente o comportamento atual**
   - O que o código faz agora?
   - Qual é o output esperado?
   - Qual é o output real?

3. **Determine a menor correção possível**
   ```
   Escala de Intervenção:
   1. Mudar um parâmetro
   2. Adicionar uma condição
   3. Extrair método
   4. Reorganizar fluxo
   5. Reescrever módulo (ÚLTIMO RECURSO)
   ```

---

### **Step 2: Análise de Impacto**

**Antes de editar, responda:**

| Pergunta                          | Resposta Esperada               |
| --------------------------------- | ------------------------------- |
| Quantos arquivos serão alterados? | ≤ 3 (ideal: 1)                  |
| Quantas linhas serão alteradas?   | ≤ 20 (ideal: ≤ 5)               |
| Há testes cobrindo essa área?     | Verificar e preservar           |
| A mudança pode introduzir bugs?   | Listar riscos                   |
| É facilmente reversível?          | Deve ser `git checkout` simples |

---

### **Step 3: Execução Segura**

#### 🟢 **Refatorações Seguras** (Executar livremente)

```dart
// Renomear variável local
final x = getData(); → final userData = getData();

// Extrair constante
if (items.length > 10) → if (items.length > kMaxItems)

// Adicionar guard clause
if (user != null) {
  if (user.isActive) {
    // logic
  }
}
→
if (user == null) return;
if (!user.isActive) return;
// logic

// Converter .then() para async/await
fetchData().then((data) => process(data));
→
final data = await fetchData();
process(data);
```

#### 🟡 **Refatorações Moderadas** (Executar com cuidado)

```dart
// Extrair método privado
void bigMethod() {
  // 50 lines...
}
→
void bigMethod() {
  _step1();
  _step2();
  _step3();
}

// Reorganizar ordem de operações (PERIGOSO)
// Verificar se não há dependências de ordem
```

#### 🔴 **Refatorações Perigosas** (Evitar ou pedir confirmação)

```dart
// Mudar assinatura de método público
Future<void> save(Data data) → Future<bool> save(Data data)

// Alterar fluxo de async/await
// Alterar ordem de listeners/streams
// Remover código "não usado" (pode ser usado indiretamente)
// Consolidar múltiplos arquivos
```

---

### **Step 4: Validação Pós-Refatoração**

**Checklist obrigatório:**

```markdown
## ✅ Validação de Refatoração

- [ ] Comportamento idêntico ao anterior
- [ ] Nenhum erro de compilação
- [ ] Nenhum warning novo do analyzer
- [ ] Hot restart funciona normalmente
- [ ] Funcionalidade principal testada manualmente
- [ ] Git diff mostra apenas mudanças intencionais
```

---

## 📋 **Templates de Refatoração**

### Template: Correção Cirúrgica

````markdown
## 🔧 Correção Cirúrgica

**Problema:** [descrição específica]
**Causa Raiz:** [por que acontece]
**Correção:** [1-3 linhas de código]

**Arquivos Alterados:** 1
**Linhas Modificadas:** [N]

**Antes:**

```dart
[código original]
```
````

**Depois:**

```dart
[código corrigido]
```

**Validação:**

- [x] Problema resolvido
- [x] Sem regressões

````

### Template: Refatoração Moderada

```markdown
## 🔧 Refatoração

**Objetivo:** [o que está sendo melhorado]
**Justificativa:** [por que é necessário]
**Riscos:** [potenciais problemas]

**Arquivos Alterados:** [lista]
**Linhas Modificadas:** [N]

**Plano de Execução:**
1. [passo 1]
2. [passo 2]
3. [validação]

**Rollback:** `git checkout HEAD -- [arquivos]`
````

---

## ⚠️ **Anti-Patterns (EVITAR)**

### ❌ **Refatoração em Cascata**

```
Problema: Bug no login
→ "Vou melhorar a arquitetura de auth primeiro"
→ "Preciso ajustar o state management"
→ "Melhor reescrever o sync"
→ 2 horas depois: 5 novos bugs, problema original não resolvido
```

**Solução:** Resolver o bug PRIMEIRO, refatorar DEPOIS (se necessário).

### ❌ **Otimização Prematura**

```
"Este código poderia ser mais eficiente..."
→ Reescreve algoritmo complexo
→ Introduz bug sutil
→ Performance melhora 0.01ms (imperceptível)
```

**Solução:** Só otimizar quando há problema mensurável de performance.

### ❌ **Perfeccionismo Estético**

```
"Não gosto desse estilo de código..."
→ Reformata arquivo inteiro
→ Git diff ilegível
→ Conflitos de merge inevitáveis
```

**Solução:** Deixar o linter cuidar de estilo. Focar em correção.

---

## 🔧 **Exemplos Práticos (Projeto Tô de Plantão)**

### Exemplo 1: Correção de Race Condition (CERTO)

```dart
// ❌ Problema: UI mostra dados incompletos
_isarSubscription = _isarRepo.watchEscalas().listen(_handleEscalasUpdate);

// ✅ Correção Cirúrgica (3 linhas)
_isarSubscription = _isarRepo.watchEscalas().listen((escalas) {
  if (syncService.isSyncing.value) return; // Guard clause
  _handleEscalasUpdate(escalas);
});
```

### Exemplo 2: Evitando Refatoração Desnecessária (CERTO)

```dart
// Problema: fireImmediately:true causa bug

// ❌ ERRADO: Reescrever toda a arquitetura de sync
// "Vamos separar o fluxo de login em 3 fases..."
// (2 horas, 5 bugs novos)

// ✅ CERTO: Mudança de 1 parâmetro
watch(fireImmediately: true) → watch(fireImmediately: false)
```

---

## 📌 **Trigger**

Ativar quando:

- Antes de refatorar qualquer código
- Quando tentado a "melhorar" código funcionando
- Após sessão de debug longa (validar se correção é mínima)

**Uso:**

```
Preciso refatorar lib/main_controller/main_auth_controller.dart
```

**Resposta esperada:**

1. Qual é o problema específico?
2. Qual é a menor correção possível?
3. Plano com análise de impacto
4. Confirmação antes de executar

---

## 🔄 **Lição Desta Sessão**

> **O que aconteceu:** 2 horas debugando problema simples porque a primeira "correção" escalou em refatoração complexa.
>
> **O que deveria ter acontecido:** 15 minutos, 3 linhas alteradas.
>
> **Aprendizado:** Correção cirúrgica primeiro. Sempre.
