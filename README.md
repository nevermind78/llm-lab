# LLM Lab — kit de TP AWS Academy

Un LLM ouvert servi par Ollama sur une instance EC2, une API FastAPI, une interface web de test,
un modèle CloudFormation et un pipeline GitHub Actions (tests, image dans ECR, déploiement).

| Chemin | Rôle | Lab |
| --- | --- | --- |
| `app/main.py` | API : `/`, `/api/health`, `/api/chat` (réponse en flux) | 2 |
| `app/static/index.html` | Interface de discussion | 2 |
| `app/Dockerfile`, `docker-compose.yml` | Image de l'API, pile Ollama + API | 2, 3 |
| `tests/test_api.py` | 7 tests avec un faux serveur de modèle | 5 |
| `infra/stack.yaml` | CloudFormation : groupe de sécurité + instance auto-configurée | 4 |
| `pipeline/ci-cd.yml` | Pipeline : tests, image vers ECR, déploiement, vérification. À copier dans `.github/workflows/` au lab 5 | 5 |

Vérifié le 13 novembre 2026 dans un Learner Lab réel (vue étudiant, `us-east-1`) : les labs 1 à 6 ont été
déroulés en ligne de commande, de l'instance manuelle au nettoyage. Les 7 tests passent ; `infra/stack.yaml`
passe cfn-lint.
Non vérifié : les parcours à la souris dans la console AWS et sur GitHub (Session Manager, CloudShell,
**Use this template**, éditeur web). Déroulez-les une fois avec un compte étudiant avant le cours.
