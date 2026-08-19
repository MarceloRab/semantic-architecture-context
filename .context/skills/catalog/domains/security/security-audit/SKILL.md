---
name: security-audit
description: Flutter/Dart security audit checklist. Covers OWASP Mobile Top 10, supply chain (pubspec), secrets scanning, secure storage, network security, and code patterns. Use before any release or after significant changes.
version: 2.0.0
tags:
  [security, flutter, dart, android, ios, owasp, secrets, supply-chain, release]
difficulty: advanced
estimated_time: 20-35min
phases: [R, V]
---

# Security Audit — Flutter

> **Mindset:** Pense como um atacante. Defenda como um especialista.
> **OWASP Mobile Top 10 (2023) + Supply Chain Security (2025)**

---

## When to use this skill

- Antes de qualquer release (Play Store, App Store, Web deploy)
- Após mudanças significativas em autenticação ou armazenamento de dados
- Ao integrar nova lib de terceiro ou API externa
- Quando o usuário pedir: "auditoria de segurança", "secure review", "release security check"

---

## Workflow

- [ ] **1. Supply Chain** — Verificar dependências e pubspec
- [ ] **2. Secrets Scan** — Checar secrets hardcoded no código Dart
- [ ] **3. Secure Storage** — Verificar tokens e dados sensíveis
- [ ] **4. Network Security** — TLS, pinning, interceptors
- [ ] **5. Code Patterns** — Vulnerabilidades no código Dart
- [ ] **6. Platform-Specific** — Android e iOS configs
- [ ] **7. Data Protection** — PII, logs, backups

---

## 1. Supply Chain Security (A03 — OWASP 2025)

### pubspec.yaml

```bash
# Verificar vulnerabilidades conhecidas
dart pub outdated
dart pub audit  # Requer Dart 3.4+
```

| Check                                                         | Risco                                       |
| ------------------------------------------------------------- | ------------------------------------------- |
| Deps sem versão fixada (`^` ao invés de `>=x.y.z <x.(y+1).0`) | Atualização automática pode incluir malware |
| `pubspec.lock` não commitado                                  | Equipe pode usar versões diferentes         |
| Libs sem manutenção (última atualização > 1 ano)              | Sem patches de segurança                    |
| Libs com poucos downloads/stars                               | Menor vetor de ataque por popularidade      |

```yaml
# ✅ Versão com range controlado
dependencies:
  http: ">=1.1.0 <2.0.0"

# ⚠️ Range muito amplo — pode puxar breaking changes
dependencies:
  http: ^1.1.0

# ✅ pubspec.lock DEVE estar no git
# Remova do .gitignore se estiver lá!
```

### Checklist Supply Chain

- [ ] `dart pub audit` sem vulnerabilidades críticas
- [ ] `pubspec.lock` commitado e atualizado
- [ ] Todos os pacotes com manutenção ativa (último pub < 12 meses)
- [ ] Nenhum pacote sem uso (remover de pubspec.yaml)
- [ ] Nenhum fork não-oficial de lib crítica (auth, crypto)

---

## 2. Secrets Scanning (High Priority)

### Padrões a Buscar em Código Dart

```bash
# Rodar no terminal do projeto
grep -r "api_key\|apikey\|API_KEY" lib/ --include="*.dart"
grep -r "password\|senha\|passwd" lib/ --include="*.dart"
grep -r "secret\|token\|bearer" lib/ --include="*.dart"
grep -r "firebase\|supabase\|googleapi" lib/ --include="*.dart"
grep -rE "AIza[0-9A-Za-z_-]{35}" lib/  # Google API key pattern
grep -rE "sk-[a-zA-Z0-9]{48}" lib/     # OpenAI key pattern
```

| Padrão                                       | Tipo               | Severidade |
| -------------------------------------------- | ------------------ | ---------- |
| Hardcoded URL com chave na query string      | API Key exposta    | CRITICAL   |
| `const String apiKey = "..."` no código Dart | API Key hardcoded  | CRITICAL   |
| `print()` exibindo token ou senha            | Log de credencial  | HIGH       |
| Credenciais em comentários                   | Credencial exposta | HIGH       |
| URLs de staging com auth no código           | Ambiente hardcoded | MEDIUM     |

### Uso Correto: `--dart-define`

```bash
# Build com secrets via variáveis de ambiente
flutter build apk --release \
  --dart-define=API_KEY=xxx \
  --dart-define=BASE_URL=https://api.example.com
```

```dart
// Acessar no código Dart
const apiKey = String.fromEnvironment('API_KEY');
const baseUrl = String.fromEnvironment('BASE_URL');
```

---

## 3. Secure Storage (OWASP M9 — Insecure Data Storage)

### O Que NUNCA Guardar em SharedPreferences

| Dado                       | Local Incorreto     | Local Correto                   |
| -------------------------- | ------------------- | ------------------------------- |
| Auth tokens (JWT, Bearer)  | `SharedPreferences` | `flutter_secure_storage`        |
| Refresh tokens             | `SharedPreferences` | `flutter_secure_storage`        |
| Senhas                     | Qualquer storage    | Nunca armazenar localmente      |
| PII sensível (CPF, cartão) | `SharedPreferences` | Encrypted DB ou Secure Storage  |
| Chaves de criptografia     | Código Dart         | Android Keystore / iOS Keychain |

```dart
// ❌ Errado — acessível em root/jailbreak
final prefs = await SharedPreferences.getInstance();
prefs.setString('authToken', token);

// ✅ Correto — hardware-backed encryption
const storage = FlutterSecureStorage(
  aOptions: AndroidOptions(encryptedSharedPreferences: true),
  iOptions: IOSOptions(accessibility: KeychainAccessibility.first_unlock),
);
await storage.write(key: 'authToken', value: token);
```

### Checklist Secure Storage

- [ ] Nenhum auth token em `SharedPreferences`
- [ ] `flutter_secure_storage` com opções específicas por plataforma
- [ ] Lógica de logout apaga tokens do secure storage
- [ ] Sem dados sensíveis em `hive` boxes não-criptografados
- [ ] SQLite com criptografia (sqlcipher) se armazenar PII

---

## 4. Network Security

### HTTPS e TLS

```dart
// ❌ Errado — aceita qualquer certificado
class MyHttpClient extends HttpClient {
  @override
  bool get badCertificateCallback => (X509Certificate cert, String host, int port) => true;
}

// ✅ Correto — validação estrita em produção
final dio = Dio();
// Não sobrescreva a validação de certificados!
```

### Android Network Security Config

```xml
<!-- android/app/src/main/res/xml/network_security_config.xml -->
<!-- ✅ Produção: bloquear HTTP -->
<?xml version="1.0" encoding="utf-8"?>
<network-security-config>
    <base-config cleartextTrafficPermitted="false">
        <trust-anchors>
            <certificates src="system" />
        </trust-anchors>
    </base-config>
</network-security-config>
```

```xml
<!-- AndroidManifest.xml -->
<application
    android:networkSecurityConfig="@xml/network_security_config"
    ... >
```

### Checklist Network

- [ ] Nenhum `http://` em URLs de produção (apenas `https://`)
- [ ] Nenhum `badCertificateCallback` que retorna `true` em produção
- [ ] Sem `android:usesCleartextTraffic="true"` no `AndroidManifest.xml` (ou apenas debug)
- [ ] Interceptors de auth verificam expiração de token antes de fazer request
- [ ] Timeout configurado nos clients HTTP (evitar hang requests)

---

## 5. Code Patterns Vulneráveis

### Injection Risks

```dart
// ❌ Injection em SQLite
final result = await db.rawQuery(
  'SELECT * FROM users WHERE name = "$userInput"' // INJECTION!
);

// ✅ Parâmetros seguros
final result = await db.rawQuery(
  'SELECT * FROM users WHERE name = ?',
  [userInput]
);
```

### DeepLinks e Intent Handling

```dart
// Sempre validar deeplinks antes de processar
void handleDeepLink(Uri uri) {
  // ✅ Whitelist de paths permitidos
  const allowedPaths = ['/home', '/product', '/category'];
  if (!allowedPaths.contains(uri.path)) {
    debugPrint('⚠️ [DeepLink] Path suspeito bloqueado: ${uri.path}');
    return;
  }

  // ✅ Sanitizar parâmetros — nunca executar como código
  final id = uri.queryParameters['id'];
  if (id != null && RegExp(r'^[a-zA-Z0-9-]+$').hasMatch(id)) {
    navigateToProduct(id);
  }
}
```

### Serialização

```dart
// ⚠️ Cuidado com fromJson de fontes não confiáveis
// Sempre validar campos obrigatórios antes de usar
// Nunca executar conteúdo de dados externos
```

---

## 6. Platform-Specific

### Android

| Check                                               | Onde Verificar                              |
| --------------------------------------------------- | ------------------------------------------- |
| `android:exported` em components desnecessários     | `AndroidManifest.xml`                       |
| `android:debuggable="false"` em release             | `build.gradle.kts` (automático em release)  |
| ProGuard/R8 habilitado em release                   | `buildTypes.release.isMinifyEnabled = true` |
| Permissões mínimas necessárias                      | `AndroidManifest.xml`                       |
| `allowBackup="false"` para apps com dados sensíveis | `AndroidManifest.xml`                       |

```xml
<!-- ✅ Seguro para dados sensíveis -->
<application
    android:allowBackup="false"
    android:fullBackupContent="false"
    ... >
```

### iOS

| Check                                        | Onde Verificar                 |
| -------------------------------------------- | ------------------------------ |
| ATS habilitado (sem exceções desnecessárias) | `Info.plist`                   |
| Permissões com descrição real                | `Info.plist` (privacy strings) |
| Sem credenciais em `Info.plist`              | `Info.plist`                   |
| Keychain data com `accessible` correto       | Código Swift/Dart              |
| JailBreak detection se necessário            | lib específica                 |

```xml
<!-- ✅ ATS sem exceções -->
<!-- NÃO adicione NSAppTransportSecurity exceptions em produção -->
```

---

## 7. Data Protection

### Logs e Debugging

```dart
// ❌ Log de dado sensível
debugPrint('🚀 [AuthService.login] <token> $authToken'); // Expõe token!
debugPrint('🚀 [PaymentService] <cardNumber> $cardNumber'); // PII!

// ✅ Log mascarado
debugPrint('✅ [AuthService.login] <token_received> ${authToken.isNotEmpty}');
debugPrint('✅ [PaymentService] <card> **** **** **** ${cardNumber.substring(12)}');
```

### LGPD/GDPR Checklist

- [ ] Dados pessoais identificados e documentados
- [ ] Consentimento implementado para coleta de dados
- [ ] Usuário pode exportar ou deletar dados (right to erasure)
- [ ] Analytics anonimizados (sem PII em eventos)
- [ ] Política de privacidade linkada no app

---

## 8. Output Template — Security Report

Ao finalizar a auditoria, entregar:

```markdown
## Security Audit Report

**Data:** [data]
**Versão:** [versão do app]

### 🔴 CRITICAL (Bloqueadores de Release)

- [item] — [arquivo:linha] — Fix: [ação]

### 🟠 HIGH

- [item] — [arquivo:linha] — Fix: [ação]

### 🟡 MEDIUM

- [item] — Fix: [ação]

### 🟢 LOW

- [item] — Aceitar ou corrigir

### ✅ Veredicto

[ ] APROVADO — Nenhum critical/high encontrado
[ ] BLOQUEADO — Corrija os critical antes do release
```

---

## Anti-Patterns

| ❌ Não Faça                        | ✅ Faça                         |
| ---------------------------------- | ------------------------------- |
| Guardar token em SharedPreferences | `flutter_secure_storage`        |
| Usar HTTP em produção              | HTTPS obrigatório               |
| `badCertificateCallback` = true    | Nunca desabilitar validação SSL |
| API keys hardcoded no Dart         | `--dart-define` + CI secrets    |
| print() com dados sensíveis        | Mascarar ou remover os logs     |
| pubspec.lock no .gitignore         | Commitar o lock file            |
| Aceitar qualquer deeplink          | Whitelist de paths permitidos   |
| Permissões desnecessárias          | Princípio do menor privilégio   |

---

## Related Skills

- `deployment-flutter` — Checar configurações de build antes do release
- `reviewing-code-changes` — Incluir security checks no code review
- `investigating-bugs` — Para vulnerabilidades reportadas
- `validating-flutter-projects` — Validação completa de projeto

## Validation Script

```bash
# Executar audit de dependências
dart pub audit

# Buscar secrets hardcoded
grep -rE "(api_key|apiKey|API_KEY|secret|password|token)" lib/ --include="*.dart" | grep -v "_test.dart"

# Verificar package desatualizado
dart pub outdated
```
