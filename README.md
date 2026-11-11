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

Vérifié par l'auteur : les 7 tests passent ; `infra/stack.yaml` passe cfn-lint.
Non exécuté par l'auteur : le déploiement réel dans un Learner Lab (EC2, ECR, exécuteur GitHub).
Déroulez les labs 0 à 6 une fois avec un compte étudiant avant le cours.
