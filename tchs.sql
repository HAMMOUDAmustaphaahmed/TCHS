-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Hôte : 127.0.0.1
-- Généré le : mar. 21 jan. 2025 à 17:17
-- Version du serveur : 10.4.32-MariaDB
-- Version de PHP : 8.0.30

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de données : `tchs`
--

-- --------------------------------------------------------

--
-- Structure de la table `adherent`
--

CREATE TABLE `adherent` (
  `adherent_id` int(11) NOT NULL,
  `nom` varchar(100) NOT NULL,
  `prenom` varchar(100) NOT NULL,
  `date_naissance` date NOT NULL,
  `sexe` enum('M','F') NOT NULL,
  `date_inscription` date NOT NULL,
  `tel1` varchar(20) DEFAULT NULL,
  `tel2` varchar(20) DEFAULT NULL,
  `type_abonnement` varchar(50) DEFAULT NULL,
  `ancien_abonne` varchar(50) NOT NULL,
  `matricule` int(11) DEFAULT NULL,
  `groupe` varchar(50) DEFAULT NULL,
  `entraineur` varchar(50) DEFAULT NULL,
  `email` varchar(100) DEFAULT NULL,
  `paye` enum('O','N') NOT NULL,
  `status` enum('Actif','Non-Actif') NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `adherent`
--

INSERT INTO `adherent` (`adherent_id`, `nom`, `prenom`, `date_naissance`, `sexe`, `date_inscription`, `tel1`, `tel2`, `type_abonnement`, `ancien_abonne`, `matricule`, `groupe`, `entraineur`, `email`, `paye`, `status`) VALUES
(6, 'hammouda', 'ahmed', '1996-08-30', 'M', '2025-01-20', '54391747', '54391747', 'Loisir', 'Non', 1, 'john.doe', 'john doe', 'ahmed@gmail.com', 'N', 'Actif'),
(7, 'mohamed', 'ali', '1990-01-01', 'M', '2025-01-20', '12345678', '123546789', 'Loisir', 'Non', 2, 'john.doe', 'john doe', 'user@gmail.com', 'N', 'Actif'),
(8, 'mohamed', 'saleh', '1994-01-01', 'M', '2025-01-20', '1234', '12345', 'Loisir', 'Non', 3, 'john.doe', 'john doe', 'user@gmail.com', 'N', 'Actif');

-- --------------------------------------------------------

--
-- Structure de la table `bon_de_recette`
--

CREATE TABLE `bon_de_recette` (
  `id_bon` int(11) NOT NULL,
  `libelle_bon` varchar(255) DEFAULT NULL,
  `nom_adherent` varchar(100) DEFAULT NULL,
  `prenom_adherent` varchar(100) DEFAULT NULL,
  `type_reglement` varchar(50) DEFAULT NULL,
  `matricule` int(11) DEFAULT NULL,
  `n_cheque` varchar(50) DEFAULT NULL,
  `banque` varchar(100) DEFAULT NULL,
  `date_echeance` date DEFAULT NULL,
  `date_inscription` date NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `bon_de_recette`
--

INSERT INTO `bon_de_recette` (`id_bon`, `libelle_bon`, `nom_adherent`, `prenom_adherent`, `type_reglement`, `matricule`, `n_cheque`, `banque`, `date_echeance`, `date_inscription`) VALUES
(1, 'Loisir', 'zefz', 'azfazd', 'Cheque', 124, '1315615616', 'BIAT', NULL, '2025-01-16'),
(2, 'Ecole', 'test', 'test', 'Cheque', 125, '144665161616', 'qsc', NULL, '2025-01-16'),
(3, 'Adulte', 'abdelmaksoud', 'thameur', 'Cheque', 4, '0001111', 'aaa', NULL, '2025-01-17');

-- --------------------------------------------------------

--
-- Structure de la table `depense`
--

CREATE TABLE `depense` (
  `id` int(11) NOT NULL,
  `libelle` varchar(255) NOT NULL,
  `montant` decimal(10,2) NOT NULL,
  `date` date NOT NULL,
  `type_depense` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Structure de la table `entraineur`
--

CREATE TABLE `entraineur` (
  `id_entraineur` int(11) NOT NULL,
  `nom` varchar(100) NOT NULL,
  `prenom` varchar(100) NOT NULL,
  `sexe` enum('M','F') NOT NULL,
  `type_abonnement` varchar(50) DEFAULT NULL,
  `enfant` enum('Oui','Non') DEFAULT NULL,
  `status` enum('Actif','Non-Actif') NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `entraineur`
--

INSERT INTO `entraineur` (`id_entraineur`, `nom`, `prenom`, `sexe`, `type_abonnement`, `enfant`, `status`) VALUES
(1, 'test', 'tedst', 'M', 'N/D', 'Non', 'Actif'),
(10, 'john', 'doe', 'M', 'Loisir', 'Oui', 'Actif');

-- --------------------------------------------------------

--
-- Structure de la table `groupe`
--

CREATE TABLE `groupe` (
  `id_groupe` int(11) NOT NULL,
  `nom_groupe` varchar(100) NOT NULL,
  `entraineur_nom` varchar(50) NOT NULL,
  `type_abonnement` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `groupe`
--

INSERT INTO `groupe` (`id_groupe`, `nom_groupe`, `entraineur_nom`, `type_abonnement`) VALUES
(1, 'john.doe', 'john doe', 'Loisir'),
(2, 'john.doe2', 'john doe', 'Loisir');

-- --------------------------------------------------------

--
-- Structure de la table `messages`
--

CREATE TABLE `messages` (
  `id` int(11) NOT NULL,
  `expediteur` varchar(255) NOT NULL,
  `destinataires` varchar(255) NOT NULL,
  `objet` varchar(100) NOT NULL,
  `corps` text NOT NULL,
  `date_envoi` datetime DEFAULT current_timestamp(),
  `statut` varchar(50) DEFAULT 'non lu'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `messages`
--

INSERT INTO `messages` (`id`, `expediteur`, `destinataires`, `objet`, `corps`, `date_envoi`, `statut`) VALUES
(4, 'john.doe', '', 'test', 'test', '2025-01-20 14:01:23', 'non lu'),
(5, 'john.doe', ',admin', 'test2', 'test2', '2025-01-20 14:02:37', 'non lu'),
(6, 'john.doe', ',admin,manager', 'test3', 'test3', '2025-01-20 14:03:04', 'non lu'),
(7, 'john.doe', 'admin', 'a', 'a', '2025-01-20 15:11:04', 'non lu'),
(8, 'admin', '', 'aaaa', 'aaaa', '2025-01-20 15:47:45', 'non lu'),
(9, 'admin', '', 'hello', 'hello', '2025-01-21 07:08:03', 'non lu');

-- --------------------------------------------------------

--
-- Structure de la table `presence`
--

CREATE TABLE `presence` (
  `id_presence` int(11) NOT NULL,
  `groupe_nom` varchar(100) NOT NULL,
  `adherent_matricule` varchar(50) NOT NULL,
  `entraineur_nom` varchar(100) NOT NULL,
  `date_seance` date NOT NULL,
  `heure_debut` time NOT NULL,
  `heure_fin` time NOT NULL,
  `est_present` enum('O','N') NOT NULL DEFAULT 'N'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Structure de la table `revenu`
--

CREATE TABLE `revenu` (
  `id` int(11) NOT NULL,
  `libelle` varchar(255) NOT NULL,
  `montant` decimal(10,2) NOT NULL,
  `date` date NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Structure de la table `seances`
--

CREATE TABLE `seances` (
  `seance_id` int(11) NOT NULL,
  `date` date NOT NULL,
  `heure` time NOT NULL,
  `groupe` varchar(100) NOT NULL,
  `entraineur` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `seances`
--

INSERT INTO `seances` (`seance_id`, `date`, `heure`, `groupe`, `entraineur`) VALUES
(1, '2025-01-01', '11:30:00', 'john.doe', 'john doe'),
(2, '2025-01-01', '11:30:00', 'john.doe', 'john doe');

-- --------------------------------------------------------

--
-- Structure de la table `utilisateurs`
--

CREATE TABLE `utilisateurs` (
  `id` int(11) NOT NULL,
  `utilisateur` varchar(50) NOT NULL,
  `password` varchar(255) NOT NULL,
  `role` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `utilisateurs`
--

INSERT INTO `utilisateurs` (`id`, `utilisateur`, `password`, `role`) VALUES
(1, 'admin', '8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918', 'admin'),
(3, 'manager', '32ccf5889dcae26d988e57e9d9c9abea9ce9eb2cc541153b18c6ee9ef8855182', 'admin'),
(6, 'john.doe', 'a18ceb2154111dd7e9bdfe59a36ae187ef6880bdbe676fb47ca1bb796f3dcbc1', 'entraineur');

--
-- Index pour les tables déchargées
--

--
-- Index pour la table `adherent`
--
ALTER TABLE `adherent`
  ADD PRIMARY KEY (`adherent_id`);

--
-- Index pour la table `bon_de_recette`
--
ALTER TABLE `bon_de_recette`
  ADD PRIMARY KEY (`id_bon`);

--
-- Index pour la table `depense`
--
ALTER TABLE `depense`
  ADD PRIMARY KEY (`id`);

--
-- Index pour la table `entraineur`
--
ALTER TABLE `entraineur`
  ADD PRIMARY KEY (`id_entraineur`);

--
-- Index pour la table `groupe`
--
ALTER TABLE `groupe`
  ADD PRIMARY KEY (`id_groupe`);

--
-- Index pour la table `messages`
--
ALTER TABLE `messages`
  ADD PRIMARY KEY (`id`);

--
-- Index pour la table `presence`
--
ALTER TABLE `presence`
  ADD PRIMARY KEY (`id_presence`);

--
-- Index pour la table `revenu`
--
ALTER TABLE `revenu`
  ADD PRIMARY KEY (`id`);

--
-- Index pour la table `seances`
--
ALTER TABLE `seances`
  ADD PRIMARY KEY (`seance_id`);

--
-- Index pour la table `utilisateurs`
--
ALTER TABLE `utilisateurs`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT pour les tables déchargées
--

--
-- AUTO_INCREMENT pour la table `adherent`
--
ALTER TABLE `adherent`
  MODIFY `adherent_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=9;

--
-- AUTO_INCREMENT pour la table `bon_de_recette`
--
ALTER TABLE `bon_de_recette`
  MODIFY `id_bon` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT pour la table `depense`
--
ALTER TABLE `depense`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT pour la table `entraineur`
--
ALTER TABLE `entraineur`
  MODIFY `id_entraineur` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;

--
-- AUTO_INCREMENT pour la table `groupe`
--
ALTER TABLE `groupe`
  MODIFY `id_groupe` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT pour la table `messages`
--
ALTER TABLE `messages`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=10;

--
-- AUTO_INCREMENT pour la table `presence`
--
ALTER TABLE `presence`
  MODIFY `id_presence` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT pour la table `revenu`
--
ALTER TABLE `revenu`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT pour la table `seances`
--
ALTER TABLE `seances`
  MODIFY `seance_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT pour la table `utilisateurs`
--
ALTER TABLE `utilisateurs`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
