"""Jeu de données de spécialisation : l'assistant de Polytechnique Sousse.

Chaque fait a une réponse, quatre formulations de question pour l'entraînement
et une cinquième, jamais vue à l'entraînement, pour l'évaluation.

Source des faits : pages publiques de https://www.polytecsousse.tn consultées le 13 novembre 2026.
À FAIRE VALIDER PAR L'ÉCOLE avant tout usage réel : les frais et les listes changent chaque année.

Usage : python donnees.py   ->  écrit train.jsonl et test.jsonl
"""
import json
import random

SYSTEME = ("Tu es l'assistant de Polytechnique Sousse (École Polytechnique de Sousse, Tunisie). "
           "Réponds en français, de façon concise et exacte. "
           "Si tu ne connais pas une information, dis-le et renvoie vers le service admission.")

CONTACT = "le service admission au (+216) 73 277 877 ou par e-mail à contact@polytecsousse.tn"

# (réponse, [4 questions d'entraînement], question de test)
FAITS = [
    # --- Identité et contact ---
    ("Polytechnique Sousse, ou École Polytechnique de Sousse (EPS), est un établissement privé d'enseignement supérieur situé à Sousse, en Tunisie. Elle forme des ingénieurs et des architectes, et propose aussi un cycle préparatoire et des licences.",
     ["C'est quoi Polytechnique Sousse ?", "Présente-moi l'École Polytechnique de Sousse.", "Que signifie EPS ?", "Polytechnique Sousse, c'est quel genre d'école ?"],
     "Peux-tu me décrire l'EPS en deux phrases ?"),
    ("L'école se trouve Route Ceinture Sahloul, Entrée Kalaa Sghira, 4021 Sousse, Tunisie.",
     ["Quelle est l'adresse de Polytechnique Sousse ?", "Où se trouve l'école ?", "Où est situé le campus de l'EPS ?", "Donne-moi l'adresse postale de l'école."],
     "L'école est à quel endroit exactement ?"),
    ("Le service admission et commercial répond au (+216) 73 277 877, au (+216) 99 277 877 et au (+216) 96 277 877.",
     ["Quel est le numéro de téléphone de l'école ?", "Comment joindre le service admission par téléphone ?", "Je veux appeler Polytechnique Sousse, quel numéro ?", "Numéro de tel de l'EPS svp"],
     "À quel numéro puis-je appeler l'admission ?"),
    ("L'adresse e-mail de l'école est contact@polytecsousse.tn.",
     ["Quelle est l'adresse e-mail de Polytechnique Sousse ?", "À quelle adresse mail écrire à l'école ?", "Comment contacter l'EPS par e-mail ?", "Email de contact de l'école ?"],
     "Je veux envoyer un mail à l'école, quelle adresse ?"),
    ("Le site officiel est www.polytecsousse.tn.",
     ["Quel est le site web de Polytechnique Sousse ?", "Où trouver le site officiel de l'école ?", "L'EPS a-t-elle un site internet ?", "Donne-moi l'adresse du site de l'école."],
     "C'est quoi le site internet de l'EPS ?"),
    ("Oui. Polytechnique Sousse est une institution agréée par l'État, sous le numéro d'agrément 02-2009.",
     ["Polytechnique Sousse est-elle agréée par l'État ?", "Quel est le numéro d'agrément de l'école ?", "L'EPS est-elle une école reconnue ?", "L'école a-t-elle un agrément du ministère ?"],
     "Est-ce que l'école est agréée, et sous quel numéro ?"),
    ("Polytechnique Sousse regroupe Poly École d'ingénieurs, Poly Digital School, Poly Préparatoire, Poly Architecture et le centre Poly Formation & Certification (POLYFC). L'Estim Business School partage le même campus.",
     ["Quelles sont les écoles de Polytechnique Sousse ?", "Comment l'EPS est-elle organisée ?", "Quelles structures composent Polytechnique Sousse ?", "Quelles sont les différentes entités de l'école ?"],
     "De quelles écoles se compose Polytechnique Sousse ?"),
    ("L'Estim Business School est l'école de commerce installée sur le même campus. Elle enseigne le management, la finance, le marketing et la comptabilité. Son site est www.estim.tn.",
     ["C'est quoi l'Estim Business School ?", "Qu'enseigne-t-on à l'Estim ?", "Y a-t-il une école de commerce sur le campus ?", "Quel est le lien entre Estim et Polytechnique Sousse ?"],
     "Parle-moi de l'Estim."),

    # --- Formations ---
    ("Le cycle ingénieur propose le Génie Informatique, le Génie Biotechnologique, le Génie Civil, le Génie Électrique et Automatique et le Génie Électromécanique. La page de l'école d'ingénieurs cite aussi le Génie Mécanique et le Génie Mathématiques appliquées.",
     ["Quelles sont les filières d'ingénieur à Polytechnique Sousse ?", "Quelles spécialités d'ingénieur propose l'école ?", "Quels génies peut-on étudier à l'EPS ?", "Liste des formations d'ingénieur de l'école ?"],
     "Quels diplômes d'ingénieur puis-je préparer à l'EPS ?"),
    ("Le Génie Informatique propose cinq parcours : Génie Logiciel, Data Science & IA, Business Intelligence, Cybersécurité et Internet of Things (IoT).",
     ["Quels sont les parcours du Génie Informatique ?", "Quelles spécialités en informatique à Polytechnique Sousse ?", "Peut-on étudier la cybersécurité ou la data science à l'EPS ?", "Quelles options en génie informatique ?"],
     "En génie info, quelles spécialisations sont proposées ?"),
    ("En Génie Informatique, les semestres S1, S2 et S3 forment un tronc commun. L'étudiant choisit sa spécialité au semestre S4, en deuxième année.",
     ["Quand choisit-on sa spécialité en Génie Informatique ?", "Y a-t-il un tronc commun en génie informatique ?", "À quel semestre se fait le choix du parcours informatique ?", "Comment est organisé le cycle ingénieur en informatique ?"],
     "À partir de quand je me spécialise en génie informatique ?"),
    ("La première année du cycle ingénieur est ouverte, sur dossier, aux titulaires d'un Bac+2 ou d'un Bac+3 : cycle préparatoire, concours national validé, licence, maîtrise ou équivalent.",
     ["Quelles sont les conditions d'admission en cycle ingénieur ?", "Comment entrer en première année d'ingénieur à l'EPS ?", "Avec quel diplôme peut-on intégrer le cycle ingénieur ?", "L'admission en école d'ingénieurs se fait-elle sur concours ou sur dossier ?"],
     "J'ai une licence, puis-je intégrer le cycle ingénieur ?"),
    ("Oui. Les étudiants ayant validé au minimum un Master 1 peuvent s'inscrire directement en deuxième année du cycle ingénieur.",
     ["Peut-on entrer directement en deuxième année du cycle ingénieur ?", "J'ai un master 1, en quelle année puis-je entrer ?", "Qui peut intégrer la 2e année d'ingénieur ?", "Y a-t-il une admission parallèle en deuxième année ?"],
     "Avec un M1, est-ce que je saute la première année d'ingénieur ?"),
    ("Poly Digital School est l'école de Polytechnique Sousse dédiée au numérique : données, cybersécurité et Business Intelligence. Elle propose une préparatoire TIC, des licences et le cycle ingénieur en Génie Informatique.",
     ["C'est quoi Poly Digital School ?", "Que propose la Poly Digital School ?", "Quelle école de l'EPS est spécialisée dans le numérique ?", "Présente-moi Poly Digital School."],
     "À quoi sert Poly Digital School ?"),
    ("Un nouveau bachelier scientifique peut intégrer Poly Digital School en Prépa TIC ou en licence, par exemple en Business Intelligence ou en Génie Logiciel. Il peut aussi choisir le cycle préparatoire ou l'architecture.",
     ["Je viens d'avoir mon bac, que puis-je faire à Polytechnique Sousse ?", "Quelles formations après le bac à l'EPS ?", "Où peut s'inscrire un nouveau bachelier ?", "Que propose l'école aux bacheliers scientifiques ?"],
     "Avec un bac scientifique, dans quoi puis-je m'inscrire ?"),
    ("L'école propose les licences Génie Logiciel et Système d'Information, Business Intelligence, Big Data et Analyse des Données, Réseaux et Cybersécurité, et Bioressources et Économie Circulaire. Le site cite aussi les licences ECVI et ARI.",
     ["Quelles licences propose Polytechnique Sousse ?", "Peut-on faire une licence à l'EPS ?", "Quelles sont les licences en informatique de l'école ?", "Liste des licences disponibles ?"],
     "Y a-t-il des licences, et lesquelles ?"),
    ("Le cycle préparatoire dure deux ans et l'accès se fait sur dossier. Trois formules existent : préparatoire intégrée, préparatoire TIC et préparatoire classique.",
     ["Comment fonctionne le cycle préparatoire ?", "Combien de temps dure la prépa à Polytechnique Sousse ?", "Quels types de préparatoire propose l'école ?", "C'est quoi Poly Préparatoire ?"],
     "La prépa dure combien d'années et il y en a combien de sortes ?"),
    ("La formation en architecture dure six ans. Elle est ouverte aux bacheliers, sur dossier. L'École d'Architecture est agréée par l'État depuis le 12 juin 2014.",
     ["Combien de temps durent les études d'architecture ?", "Comment entrer à l'école d'architecture ?", "L'école d'architecture est-elle agréée ?", "Présente-moi Poly Architecture."],
     "L'architecture à l'EPS, c'est combien d'années et depuis quand est-elle agréée ?"),
    ("Les études d'architecture combinent cours théoriques, ateliers, projets personnels, voyages d'études, stages et séminaires. En sixième année, l'étudiant effectue un stage en bureau d'études ou d'urbanisme.",
     ["Comment se déroulent les études d'architecture ?", "Que fait-on en sixième année d'architecture ?", "Y a-t-il des stages en architecture ?", "Quel est le contenu de la formation d'architecte ?"],
     "De quoi est faite la formation en architecture ?"),
    ("Les diplômés en architecture peuvent s'inscrire à l'Ordre des Architectes de Tunisie (OAT). Ils deviennent architectes, cadres dans des institutions publiques, enseignants du supérieur ou architectes paysagistes.",
     ["Quels sont les débouchés après l'école d'architecture ?", "Peut-on s'inscrire à l'Ordre des Architectes après l'EPS ?", "Quels métiers après des études d'architecture à Polytechnique Sousse ?", "Que devient-on après Poly Architecture ?"],
     "Après le diplôme d'architecte, quelles carrières sont possibles ?"),

    # --- Accréditation ---
    ("Oui. Polytechnique Sousse détient l'accréditation EUR-ACE, un label européen de qualité des formations d'ingénieur géré par l'ENAEE. L'école l'a obtenue par la Commission des Titres d'Ingénieur (CTI).",
     ["Polytechnique Sousse est-elle accréditée EUR-ACE ?", "Quelles accréditations possède l'école ?", "C'est quoi le label EUR-ACE de l'EPS ?", "L'école est-elle accréditée par la CTI ?"],
     "L'EPS a-t-elle un label de qualité européen ?"),
    ("Le label EUR-ACE apporte une reconnaissance internationale du diplôme d'ingénieur. Il facilite la mobilité académique et professionnelle, notamment en Europe, et atteste que la formation respecte les standards internationaux.",
     ["À quoi sert l'accréditation EUR-ACE ?", "Quel est l'avantage du label EUR-ACE pour un étudiant ?", "Mon diplôme sera-t-il reconnu à l'étranger ?", "Le diplôme d'ingénieur de l'EPS est-il reconnu en Europe ?"],
     "Qu'est-ce que EUR-ACE change pour mon diplôme ?"),

    # --- Frais 2026/2027 ---
    ("Pour l'année 2026/2027, le cycle préparatoire coûte 6 950 DT par an pour un étudiant tunisien, en trois tranches de 2 850, 2 450 et 1 650 DT.",
     ["Combien coûte le cycle préparatoire ?", "Quels sont les frais de la prépa à Polytechnique Sousse ?", "Prix d'une année de préparatoire ?", "Combien paie un étudiant tunisien en prépa ?"],
     "La prépa, ça revient à combien par an ?"),
    ("Pour l'année 2026/2027, le cycle ingénieur coûte 7 849 DT par an pour un étudiant tunisien, en trois tranches de 3 250, 2 700 et 1 899 DT.",
     ["Combien coûte le cycle ingénieur ?", "Quels sont les frais de scolarité en école d'ingénieurs ?", "Prix d'une année d'ingénieur à l'EPS ?", "Combien paie un étudiant tunisien en cycle ingénieur ?"],
     "Une année d'ingénieur, c'est combien ?"),
    ("Pour l'année 2026/2027, la licence coûte 6 629 DT par an pour un étudiant tunisien, en trois tranches de 2 750, 2 500 et 1 379 DT.",
     ["Combien coûte une licence à Polytechnique Sousse ?", "Quels sont les frais du cycle licence ?", "Prix d'une année de licence ?", "Combien paie un étudiant tunisien en licence ?"],
     "La licence coûte combien par année ?"),
    ("Pour l'année 2026/2027, les frais d'architecture pour un étudiant tunisien vont de 6 987 DT en première année à 8 100 DT en sixième année : 7 240 DT en 2e, 7 460 DT en 3e, 7 670 DT en 4e et 7 880 DT en 5e année.",
     ["Combien coûtent les études d'architecture ?", "Quels sont les frais de l'école d'architecture ?", "Prix de la première année d'architecture ?", "Les frais d'architecture augmentent-ils chaque année ?"],
     "L'architecture, c'est quel budget par an ?"),
    ("Pour l'année 2026/2027, un étudiant international paie 2 889 € par an en cycle préparatoire ou en licence, 3 210 € par an en cycle ingénieur, et de 3 638 € à 4 708 € par an en architecture selon l'année.",
     ["Quels sont les frais pour les étudiants étrangers ?", "Combien paie un étudiant international à Polytechnique Sousse ?", "Frais de scolarité en euros ?", "Je ne suis pas tunisien, combien coûte le cycle ingénieur ?"],
     "Je viens de l'étranger, quels tarifs s'appliquent ?"),
    ("Les frais de dossier s'élèvent à 350 DT pour les étudiants tunisiens et à 120 € pour les étudiants internationaux. Ils sont à payer dès l'inscription et ne sont pas remboursables.",
     ["Y a-t-il des frais de dossier ?", "Combien coûtent les frais de dossier ?", "Les frais de dossier sont-ils remboursables ?", "Que faut-il payer au moment de l'inscription ?"],
     "C'est combien, les frais de dossier ?"),
    ("Les frais se règlent en trois tranches : la première à l'inscription, la deuxième avant le 31 décembre et la troisième avant le 31 mars. Une tranche n'est payable qu'une fois la précédente soldée.",
     ["Peut-on payer les frais en plusieurs fois ?", "Quel est l'échéancier de paiement ?", "Quand faut-il payer la deuxième tranche ?", "Comment sont réparties les tranches de paiement ?"],
     "Quelles sont les dates limites des tranches ?"),
    ("Oui. Le paiement intégral des frais d'inscription donne droit à une réduction de 6 %.",
     ["Y a-t-il une réduction si je paie tout d'un coup ?", "Existe-t-il des remises sur les frais ?", "Quel avantage à payer l'année en une seule fois ?", "Réduction en cas de paiement comptant ?"],
     "Si je règle toute l'année d'un coup, ai-je une remise ?"),
    ("Les frais se paient en espèces, par carte sur terminal (TPE), par chèque à l'ordre du Groupe de Formation et d'Ingénierie, ou par virement bancaire. Les coordonnées bancaires figurent sur la page « Frais d'inscription » du site.",
     ["Quels sont les modes de paiement acceptés ?", "Peut-on payer par virement ?", "À quel ordre faire le chèque ?", "Comment régler les frais de scolarité ?"],
     "Par quels moyens puis-je payer ?"),
    ("Non. L'école n'effectue aucun remboursement, et en cas d'abandon en cours d'année, tout semestre commencé reste dû.",
     ["Les frais sont-ils remboursables si j'abandonne ?", "Que se passe-t-il si j'arrête en cours d'année ?", "Peut-on être remboursé des frais de scolarité ?", "Politique de remboursement de l'école ?"],
     "Si je quitte l'école en milieu d'année, on me rembourse ?"),
    ("Les étudiants internationaux bénéficient d'un pack gratuit : l'examen DELF pour le cycle ingénieur, deux certifications pendant le cycle et une assurance maladie.",
     ["Que comprend le pack des étudiants internationaux ?", "Les étudiants étrangers ont-ils une assurance maladie ?", "Quels avantages pour les étudiants internationaux ?", "C'est quoi le pack gratuit ?"],
     "En tant qu'étudiant étranger, qu'est-ce qui est inclus dans mes frais ?"),
    ("La page des frais du site ne mentionne aucune bourse. Pour savoir si une aide existe, contactez " + CONTACT + ".",
     ["L'école propose-t-elle des bourses ?", "Peut-on avoir une bourse à Polytechnique Sousse ?", "Y a-t-il des aides financières ?", "Existe-t-il des bourses d'excellence ?"],
     "Est-ce que je peux obtenir une bourse d'études ?"),

    # --- Campus, laboratoires, certifications ---
    ("Le campus s'étend sur plus de 10 000 m², sur quatre étages répartis par spécialité, et peut accueillir plus de 3 000 étudiants. Il comprend des amphithéâtres, des salles informatiques, des laboratoires de langues et une grande cafétéria.",
     ["À quoi ressemble le campus ?", "Quelle est la superficie du campus ?", "Combien d'étudiants le campus peut-il accueillir ?", "Quels équipements trouve-t-on sur le campus ?"],
     "Décris-moi les locaux de l'école."),
    ("L'école annonce plus de 40 laboratoires. Le site présente notamment le labo MSIG de mécanique des sols, le labo électromécanique, le labo informatique, le labo Télécom & Réseau, le labo BIO, le labo de Bourse et le centre Pearson VUE.",
     ["Combien de laboratoires compte l'école ?", "Quels laboratoires y a-t-il à Polytechnique Sousse ?", "L'école a-t-elle des laboratoires spécialisés ?", "Cite-moi des laboratoires de l'EPS."],
     "Quels sont les labos de l'école ?"),
    ("Le labo de Bourse est une salle de marchés équipée de matériel et de logiciels qui permettent le trading financier en temps réel, avec les plateformes MetaTrader et TeleTrade.",
     ["C'est quoi le labo de Bourse ?", "L'école a-t-elle une salle de marchés ?", "Quels logiciels utilise le labo de Bourse ?", "Peut-on s'entraîner au trading à l'école ?"],
     "À quoi sert le laboratoire de Bourse ?"),
    ("Oui. L'école abrite un centre de test international Pearson VUE, où l'on passe des examens de certification en informatique, en intelligence artificielle et en finance.",
     ["L'école est-elle un centre Pearson VUE ?", "Où passer un examen Pearson VUE à Sousse ?", "C'est quoi le laboratoire Pearson VUE ?", "Peut-on passer des certifications sur place ?"],
     "Puis-je passer un examen de certification dans l'école même ?"),
    ("Le centre POLYFC prépare à des certifications telles que Microsoft, Cisco, Oracle, AWS, Huawei, Fortinet, IBM, PMI, CISSP, ISO 27001, ICDL, Autodesk, SolidWorks et Siemens, ainsi qu'au TOEIC et au DELF.",
     ["Quelles certifications peut-on préparer à l'école ?", "C'est quoi POLYFC ?", "Peut-on passer une certification Cisco ou AWS à Polytechnique Sousse ?", "Quelles certifications professionnelles propose l'EPS ?"],
     "Quelles certifs sont proposées par POLYFC ?"),
    ("L'école a des partenariats avec des organismes de langues qui permettent de passer les certifications DELF, DALF, TOEIC et TOEFL. Elle organise aussi des sessions TEF, TEF Canada et TEFAQ.",
     ["Quelles certifications de langue peut-on passer ?", "Peut-on passer le TOEIC ou le DELF à l'école ?", "L'école organise-t-elle le TEF Canada ?", "Y a-t-il des examens de français ou d'anglais ?"],
     "Quels tests de langue sont disponibles à l'EPS ?"),
    ("Oui. Pour les étudiants tunisiens, un examen DELF est inclus dans les frais du cycle ingénieur.",
     ["Le DELF est-il inclus dans les frais ?", "Dois-je payer le DELF en plus en cycle ingénieur ?", "L'examen de français est-il compris dans la scolarité ?", "Les élèves ingénieurs passent-ils le DELF ?"],
     "L'examen DELF est-il compris pour un élève ingénieur tunisien ?"),

    # --- Vie étudiante ---
    ("Les clubs de l'école comprennent notamment IEEE EPS, Enactus, Polyrobots, Microsoft Polytechnique Club, Google Club EPS, ACM EPS, PolySecurinets, ARSII, PolyBio, Poly Nations, Poly Auto, Tunivisions EPS, le Croissant Rouge, la radio CRIPES, le club E-Sports et le Poly ESTIM Sport Club.",
     ["Quels clubs existent à Polytechnique Sousse ?", "Y a-t-il des clubs étudiants ?", "Liste des clubs de l'EPS ?", "Quels clubs puis-je rejoindre ?"],
     "Cite-moi les clubs de l'école."),
    ("Oui. Le Club Polyrobots est le club de robotique, et PolySecurinets est le club de cybersécurité. On trouve aussi IEEE EPS, ACM EPS, le Google Club EPS et le Microsoft Polytechnique Club pour l'informatique.",
     ["Y a-t-il un club de robotique ?", "Existe-t-il un club de cybersécurité ?", "Quels clubs d'informatique à l'EPS ?", "Je m'intéresse à la robotique, quel club rejoindre ?"],
     "Quels clubs techniques pour un passionné d'informatique ?"),
    ("Les clubs sont regroupés en quatre domaines : Sciences & Technologies, Management & Entreprises, Cultures & Langues, et Art & Sport. La vie associative repose sur des événements, des formations, des projets et des concours.",
     ["Comment est organisée la vie associative ?", "Quels sont les domaines des clubs ?", "Quelles activités proposent les clubs ?", "Sur quoi repose la vie associative de l'école ?"],
     "En quelles catégories les clubs sont-ils classés ?"),
    ("Le projet socio-culturel (PSC) est un module intégré au cursus, lancé pendant l'année 2015-2016. Les étudiants y mènent un projet associatif ou culturel avec des partenaires comme des associations, des écoles primaires ou des hôpitaux.",
     ["C'est quoi le PSC ?", "Qu'est-ce que le projet socio-culturel ?", "Depuis quand le PSC existe-t-il ?", "Les étudiants font-ils des projets associatifs ?"],
     "Explique-moi le module PSC."),
    ("Les projets socio-culturels sont évalués par des experts lors d'un bal des projets socioculturels organisé par l'école. Selon le site, 82 projets ont été réalisés au cours des deux premières années.",
     ["Comment le PSC est-il évalué ?", "Combien de projets socio-culturels ont été réalisés ?", "C'est quoi le bal des projets socioculturels ?", "Qui note les projets PSC ?"],
     "Qui évalue les PSC et à quelle occasion ?"),
    ("L'incubateur GFI accompagne les étudiants, les jeunes diplômés et les anciens qui veulent créer une start-up, surtout en technologie et en ingénierie. Il offre un mentorat personnalisé, des formations, des espaces de travail équipés et l'accès à un réseau de partenaires industriels et d'investisseurs.",
     ["L'école a-t-elle un incubateur ?", "C'est quoi l'incubateur GFI ?", "Comment l'école aide-t-elle à créer une start-up ?", "Quels services propose l'incubateur ?"],
     "Je veux lancer ma start-up, l'école peut-elle m'accompagner ?"),
    ("Les demandes de documents, de stage et de projet de fin d'études (PFE) se font en ligne, depuis la rubrique « Vie Étudiante » du site.",
     ["Comment demander une convention de stage ?", "Où faire ma demande de PFE ?", "Comment obtenir une attestation ou un document ?", "Les demandes de stage se font-elles en ligne ?"],
     "Par où passe-t-on pour une demande de stage ou de PFE ?"),
    ("Les espaces numériques des étudiants, des enseignants et des parents sont accessibles à l'adresse polysys.polytecsousse.tn/espace.",
     ["Où se trouve l'espace étudiant en ligne ?", "Quelle est l'adresse de l'espace numérique ?", "Les parents ont-ils un espace en ligne ?", "Comment accéder à Polysys ?"],
     "Quel est le lien de l'espace étudiant ?"),

    # --- International ---
    ("L'école propose des doubles diplômes, des semestres d'échange dans des universités partenaires et des stages à l'étranger, notamment par le programme d'échange d'AIESEC. Elle participe aussi à des appels Erasmus.",
     ["Peut-on partir à l'étranger pendant ses études ?", "L'école propose-t-elle des doubles diplômes ?", "Y a-t-il des échanges internationaux ?", "Comment faire un stage à l'étranger ?"],
     "Quelles possibilités de mobilité internationale ?"),
    ("Le site cite parmi les partenaires internationaux CY Tech, l'UTT, l'Université de Sherbrooke, ESIGETEL, EFREI, Polytech Montpellier, Polytechnique Montréal et l'université turque Fatih Sultan Mehmet. L'école annonce plus de 100 partenariats académiques et professionnels.",
     ["Quelles sont les universités partenaires ?", "Avec quelles écoles étrangères l'EPS a-t-elle des accords ?", "Combien de partenariats possède l'école ?", "L'école a-t-elle des partenaires en France ou au Canada ?"],
     "Cite des établissements étrangers partenaires de l'EPS."),

    # --- Chiffres ---
    ("Le site annonce environ 3 000 diplômés, 250 enseignants-chercheurs, 400 projets socioculturels et plus de 40 laboratoires.",
     ["Quels sont les chiffres clés de l'école ?", "Combien de diplômés compte Polytechnique Sousse ?", "Combien d'enseignants à l'EPS ?", "Donne-moi quelques chiffres sur l'école."],
     "L'école en quelques nombres ?"),

    # --- Inscription ---
    ("La pré-inscription se fait en ligne sur www.polytecsousse.tn, rubrique « Admission ». Vous indiquez vos coordonnées, votre niveau d'études, votre spécialité, votre établissement et la formation souhaitée, puis vous validez.",
     ["Comment s'inscrire à Polytechnique Sousse ?", "Où faire la pré-inscription ?", "Quelle est la procédure d'inscription ?", "L'inscription se fait-elle en ligne ?"],
     "Quelles sont les étapes pour m'inscrire ?"),

    # --- Ce que l'assistant ne sait pas ---
    ("Je n'ai pas cette information. Le site public de l'école ne donne pas le nom de la direction dans les pages que je connais. Contactez " + CONTACT + ".",
     ["Qui est le directeur de Polytechnique Sousse ?", "Comment s'appelle le directeur de l'école ?", "Qui dirige l'EPS ?", "Quel est le nom du fondateur de l'école ?"],
     "Qui est à la tête de l'école ?"),
    ("Je n'ai pas d'information sur un foyer ou un logement étudiant : les pages du site que je connais n'en parlent pas. Contactez " + CONTACT + ".",
     ["L'école a-t-elle un foyer universitaire ?", "Peut-on être logé sur le campus ?", "Y a-t-il une résidence étudiante ?", "Comment trouver un logement près de l'école ?"],
     "Est-ce qu'il y a un internat à l'EPS ?"),
    ("Je ne connais pas les dates de rentrée ni le calendrier universitaire. Contactez " + CONTACT + ".",
     ["Quelle est la date de la rentrée ?", "Quand commencent les cours ?", "Quel est le calendrier des examens ?", "Quand ont lieu les vacances ?"],
     "La rentrée, c'est quel jour ?"),
    ("Je n'ai pas de chiffre fiable sur le taux d'insertion ou les salaires des diplômés. Contactez " + CONTACT + ".",
     ["Quel est le taux d'insertion des diplômés ?", "Quel salaire après Polytechnique Sousse ?", "Combien de diplômés trouvent un emploi ?", "Quel est le classement de l'école ?"],
     "Les diplômés trouvent-ils vite du travail, avec quel pourcentage ?"),
    ("Je suis l'assistant de Polytechnique Sousse. Je réponds aux questions sur l'école à partir des informations publiques de son site. Je peux me tromper : pour une décision importante, vérifiez auprès du service admission.",
     ["Qui es-tu ?", "À quoi sers-tu ?", "Que peux-tu faire pour moi ?", "Tu es quel assistant ?"],
     "Présente-toi."),
]


def exemple(question, reponse):
    return {"messages": [{"role": "system", "content": SYSTEME},
                         {"role": "user", "content": question},
                         {"role": "assistant", "content": reponse}]}


if __name__ == "__main__":
    train = [exemple(q, rep) for rep, questions, _ in FAITS for q in questions]
    test = [exemple(q_test, rep) for rep, _, q_test in FAITS]
    random.Random(0).shuffle(train)
    for nom, lignes in (("train.jsonl", train), ("test.jsonl", test)):
        with open(nom, "w", encoding="utf-8") as f:
            for ligne in lignes:
                f.write(json.dumps(ligne, ensure_ascii=False) + "\n")
    print(f"{len(FAITS)} faits -> {len(train)} exemples d'entraînement, {len(test)} questions de test")
