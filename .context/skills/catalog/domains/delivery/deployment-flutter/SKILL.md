---
name: deployment-flutter
description: Flutter release deployment procedures for Android (Play Store), iOS (App Store), and Web (Firebase Hosting/Vercel). Covers build signing, release checklist, and rollback strategies.
version: 1.0.0
tags:
  [delivery, deploy, flutter, android, ios, web, play-store, app-store, release]
difficulty: intermediate
estimated_time: 15-30min
---

# Deployment — Flutter

> Todo deploy é um risco. Minimize o risco com preparação, não com velocidade.

---

## When to use this skill

- Ao preparar um release Android, iOS ou Web
- Ao configurar assinatura de app pela primeira vez
- Antes de submeter para Play Store ou App Store
- Quando o usuário pedir: "gerar APK", "build de release", "subir para loja", "deploy web"

---

## Workflow Universal (5 Fases)

```
1. PREPARE   → Verificar código, build, variáveis de ambiente
2. BACKUP    → Salvar estado atual antes de mudar
3. BUILD     → Executar build de release
4. VERIFY    → Testar o artefato gerado
5. DEPLOY    → Submeter e monitorar
```

---

## Pre-Release Checklist (OBRIGATÓRIO)

- [ ] Todos os testes passando: `flutter test`
- [ ] Sem warnings: `dart analyze`
- [ ] Formatação OK: `dart format --set-exit-if-changed lib/`
- [ ] Versão atualizada em `pubspec.yaml` (`version: x.y.z+build`)
- [ ] `CHANGELOG.md` atualizado
- [ ] Variáveis de ambiente de produção configuradas
- [ ] `print()` / `debugPrint()` de debug removidos
- [ ] Chaves de API hardcoded removidas
- [ ] `flutter_dotenv` ou equivalente configurado
- [ ] Ícone e Splash Screen corretos
- [ ] Permissões de manifesto revisadas (Android/iOS)

---

## Android — Play Store

### 1. Configurar Assinatura (primeira vez)

```bash
# Gerar keystore
keytool -genkey -v -keystore release-key.jks \
  -storeAlg RSA -keysize 2048 -validity 10000 \
  -alias release-key

# ⚠️ Nunca commitar o .jks no git!
# Adicionar ao .gitignore:
# *.jks
# key.properties
```

```properties
# android/key.properties (NÃO commitar)
storePassword=<sua_senha>
keyPassword=<sua_senha>
keyAlias=release-key
storeFile=../release-key.jks
```

```kotlin
// android/app/build.gradle.kts
val keyProperties = Properties()
val keyPropertiesFile = rootProject.file("key.properties")
if (keyPropertiesFile.exists()) {
    keyProperties.load(FileInputStream(keyPropertiesFile))
}

android {
    signingConfigs {
        create("release") {
            keyAlias = keyProperties["keyAlias"] as String?
            keyPassword = keyProperties["keyPassword"] as String?
            storeFile = keyProperties["storeFile"]?.let { file(it) }
            storePassword = keyProperties["storePassword"] as String?
        }
    }
    buildTypes {
        release {
            signingConfig = signingConfigs.getByName("release")
            isMinifyEnabled = true
            isShrinkResources = true
        }
    }
}
```

### 2. Build Android

```bash
# App Bundle (recomendado para Play Store)
flutter build appbundle --release

# APK (teste em dispositivo)
flutter build apk --release --split-per-abi

# Verificar artefatos gerados
ls build/app/outputs/bundle/release/
```

### 3. Verificar Antes de Submeter

- [ ] Testar APK em dispositivo físico
- [ ] Verificar que ProGuard/R8 não quebrou nada
- [ ] Testar fluxo completo de login/onboarding
- [ ] Verificar tamanho do bundle (< 150 MB recomendado)

---

## iOS — App Store

### 1. Pré-requisitos

- Xcode instalado e atualizado
- Conta Apple Developer ativa
- Certificados e provisioning profiles configurados
- Bundle ID registrado no App Store Connect

### 2. Build iOS

```bash
# Build release
flutter build ios --release

# Via Xcode (para assinar e submeter)
open ios/Runner.xcworkspace
# Xcode → Product → Archive → Distribute App
```

### 3. Checklist iOS

- [ ] Version Number e Build Number atualizados em Xcode
- [ ] Provisioning Profile correto (Distribution)
- [ ] Todos os ícones no tamanho correto
- [ ] ATS (App Transport Security) configurado corretamente
- [ ] Permissões com descrição no `Info.plist`
- [ ] Testado em simulador E dispositivo físico

---

## Web — Firebase Hosting / Vercel

### Firebase Hosting

```bash
# Instalar Firebase CLI (se necessário)
npm install -g firebase-tools

# Login
firebase login

# Build web
flutter build web --release --base-href /

# Deploy
firebase deploy --only hosting

# Preview (sem afetar produção)
firebase hosting:channel:deploy preview
```

### Vercel

```bash
# Build
flutter build web --release

# Deploy (via CLI)
vercel --prod

# Ou configurar via vercel.json
# {
#   "buildCommand": "flutter build web --release",
#   "outputDirectory": "build/web"
# }
```

### Checklist Web

- [ ] Build com `--web-renderer html` ou `canvaskit` (escolher baseado em performance)
- [ ] PWA configurada (`manifest.json`, Service Worker)
- [ ] SQLite WASM binaries incluídos (se usar sqflite_ffi_web)
- [ ] Variáveis de ambiente via `--dart-define`
- [ ] CORS configurado no backend para o domínio

---

## Versioning (pubspec.yaml)

```yaml
# Formato: major.minor.patch+buildNumber
version: 1.2.3+45

# major: Breaking changes
# minor: Novas features (backward compatible)
# patch: Bug fixes
# buildNumber: Incrementado a cada build (Play Store/App Store exigem único)
```

```bash
# Incrementar versão via pubspec_version (opcional)
flutter pub global activate cider
cider bump patch  # 1.2.3 → 1.2.4
cider bump minor  # 1.2.3 → 1.3.0
```

---

## Rollback Strategies

| Plataforma           | Método de Rollback                                                   |
| -------------------- | -------------------------------------------------------------------- |
| **Play Store**       | Parar rollout gradual no console, reverter para versão anterior      |
| **App Store**        | Não há rollback direto; submeter nova versão rapidamente             |
| **Firebase Hosting** | `firebase hosting:clone SOURCE_SITE:SOURCE_CHANNEL TARGET_SITE:live` |
| **Vercel**           | Dashboard → Deployments → Redeploy versão anterior                   |

### Quando Fazer Rollback

| Sintoma                     | Ação              |
| --------------------------- | ----------------- |
| Crash rate > 2%             | Rollback imediato |
| Fluxo crítico quebrado      | Rollback imediato |
| Performance degradada > 30% | Avaliar rollback  |
| Bug menor isolado           | Correção forward  |

---

## Anti-Patterns

| ❌ Não Faça                         | ✅ Faça                                       |
| ----------------------------------- | --------------------------------------------- |
| Commitar `key.properties` ou `.jks` | Usar `.gitignore` + variáveis de CI           |
| Deploy sem testar em release mode   | Sempre testar o artefato final                |
| Hardcode de URLs de produção        | Usar `--dart-define` ou `.env`                |
| Pular incremento de build number    | Sempre incrementar (lojas exigem)             |
| Deploy direto sem staging           | Usar Play Store Internal Testing / TestFlight |
| `flutter build` sem `--release`     | Sempre usar `--release` para loja             |

---

## CI/CD (GitHub Actions — Referência)

```yaml
# .github/workflows/release-android.yml
name: Release Android

on:
  push:
    tags: ["v*"]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: subosito/flutter-action@v2
        with:
          flutter-version: "3.x"
      - run: flutter pub get
      - run: flutter test
      - run: flutter build appbundle --release
        env:
          KEY_STORE_PASSWORD: ${{ secrets.KEY_STORE_PASSWORD }}
          KEY_PASSWORD: ${{ secrets.KEY_PASSWORD }}
```

---

## Error Handling

### Build falha com "Execution failed for task :app:lintRelease"

- Verificar warnings do lint no Android
- Adicionar `lintOptions { disable 'InvalidPackage' }` se necessário

### "No signing certificate" iOS

- Verificar Keychain Access para certificados válidos
- Renovar provisioning profile no Apple Developer Portal

### Web: "Failed to load resource" em produção

- Verificar `--base-href` no build
- Verificar que `web/` está incluído no deploy

---

## Related Skills

- `validating-flutter-projects` — Validar projeto antes do release
- `security-audit` — Verificar segurança antes de publicar
- `commit-message` — Padronizar mensagens de commit pré-release
