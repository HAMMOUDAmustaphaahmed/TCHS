-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Hôte : 127.0.0.1
-- Généré le : mar. 28 oct. 2025 à 12:27
-- Version du serveur : 10.4.32-MariaDB
-- Version de PHP : 8.2.12

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
  `categorie` varchar(50) DEFAULT NULL,
  `matricule` int(11) DEFAULT NULL,
  `groupe` varchar(50) DEFAULT NULL,
  `entraineur` varchar(50) DEFAULT NULL,
  `email` varchar(100) DEFAULT NULL,
  `paye` enum('O','N') NOT NULL,
  `status` enum('Actif','Non-Actif') NOT NULL,
  `code_saison` varchar(10) DEFAULT NULL,
  `cotisation` float DEFAULT NULL,
  `remise` float DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `adherent`
--

INSERT INTO `adherent` (`adherent_id`, `nom`, `prenom`, `date_naissance`, `sexe`, `date_inscription`, `tel1`, `tel2`, `type_abonnement`, `categorie`, `matricule`, `groupe`, `entraineur`, `email`, `paye`, `status`, `code_saison`, `cotisation`, `remise`) VALUES
(6, 'hammouda', 'ahmed', '1996-08-30', 'M', '2025-01-20', '54391747', '54391747', 'Compétitif', 'Non', 1, NULL, NULL, 'ahmed@gmail.com', 'O', 'Actif', 'S2025', NULL, NULL),
(7, 'mohamed', 'ali', '1990-01-01', 'M', '2025-01-20', '12345678', '123546789', 'Non Compétitif', 'Non', 2, 'john.doe', 'john doe', 'user@gmail.com', 'N', 'Actif', 'S2025', NULL, NULL),
(8, 'mohamed', 'saleh', '1994-01-01', 'M', '2025-01-20', '1234', '12345', 'Non Compétitif', 'Non', 3, 'john.doe', 'john doe', 'user@gmail.com', 'N', 'Actif', 'S2025', NULL, NULL),
(9, 'Flen', 'Ben Flen', '2025-01-22', 'M', '2025-01-22', '1234', '1234', 'Non Compétitif', 'Non', 4, 'loisir', 'john doe', 'flen@gmail.com', 'N', 'Actif', 'S2025', NULL, NULL),
(10, 'Abdelmaksoud', 'Thameur', '2000-04-06', 'M', '2025-01-22', '28425595', '', 'Adulte', 'Non', 5, 'Adulte-5-A', 'Kharrat Ramzi', '', 'O', 'Actif', 'S2025', NULL, NULL),
(11, 'Foulani', 'Foulen', '2025-01-22', 'M', '2025-01-22', '1234', '', 'Compétitif', 'Non', 6, 'Lutin-1-A', 'Kharrat Ramzi', '', 'N', 'Actif', 'S2025', NULL, NULL),
(12, 'aaa', 'aaa', '2025-01-22', 'M', '2025-01-22', '134', '', 'Ecole d\'été', 'Non', 7, 'Poussin-1-B', 'Zallila Adam', 'a@gmail.com', 'N', 'Actif', 'S2025', NULL, NULL),
(13, 'Flen', 'Foulani', '2025-01-22', 'M', '2025-01-22', '1234', '', 'N/D', 'Non', 8, NULL, NULL, 'da7ee7@gmail.com', 'N', 'Actif', 'S2025', NULL, NULL),
(14, 'mohamed', 'mohamed', '1990-01-01', 'M', '2025-05-06', '12345678', '12345677', 'N/D', 'Non', 9, 'Poussin-1-A', 'Zallila Adam', 'mohamed.mohamed@gmail.com', 'N', 'Actif', 'S2025', NULL, NULL),
(15, 'Ali', 'Mohamed', '2000-01-01', 'M', '2025-08-26', '12345678', '', 'Ecole d\'été', 'Non', 10, 'Ecole d\'été-1-A', 'Mhiri Afif', '', 'O', 'Actif', 'E2025', NULL, NULL),
(16, 'Sahli', 'Ali', '2018-06-14', 'M', '2025-08-26', '28452595', '', 'Ecole d\'été', 'Oui', 11, NULL, NULL, '', 'O', 'Actif', 'E2025', 1500, 10),
(17, 'bouhlel', 'Nabil', '2017-09-25', 'M', '2025-08-26', '28452595', '', 'Compétitif', 'Oui', 12, 'Lutin-1-B', 'Kharrat Ramzi', '', 'O', 'Actif', 'E2025', NULL, NULL),
(18, 'Ben Ali', 'Saleh', '2010-01-01', 'M', '2025-08-28', '12345678', '', 'Loisir', 'Non', 13, 'Poussin-1-B', 'Zallila Adam', 'saleh.benali@gmail.com', 'N', 'Actif', 'S2025', 1300, 0),
(19, 'saleh', 'ali', '2025-09-08', 'M', '2025-09-08', '12345678', '', 'Compétitif', 'Non', 14, 'KD-1-A', 'mohamed saleh', '', 'O', 'Actif', 'S2025', 0, 0),
(20, 'adherent', 'test', '1990-01-01', 'M', '2025-09-09', '12345678', '', 'Compétitif', 'Non', 15, 'KD-1-B', NULL, 'test@gmail.com', 'O', 'Actif', 'S2025', 0, 0),
(25, 'Ayadi', 'Adel', '2025-09-23', 'M', '2025-09-23', '12345678', '', 'Loisir', 'Loisir', 16, 'Lutin-1-A', 'Kharrat Ramzi', '', 'N', 'Actif', 'S2025', 1650, 0),
(28, 'Issaoui', 'Nehed', '2025-09-23', 'M', '2025-09-23', '12345678', '', 'Ecole d\'été', 'Ecole d\'été', 19, 'Ecole_ete-2-A', 'mohamed saleh', '', 'N', 'Actif', 'S2025', 1700, 5),
(33, 'Abdelmaksoud', 'Aziz', '2012-04-06', 'M', '2024-10-01', '28425595', '', 'Compétitif', 'Compétitif', 10, 'Minime-1-A', 'Gaaloul Ilhem', 't.abdelmaksoud@gmail.com', 'N', 'Actif', 'S2025', 1200, 0);

-- --------------------------------------------------------

--
-- Structure de la table `autres_paiements`
--

CREATE TABLE `autres_paiements` (
  `id` int(11) NOT NULL,
  `nom_paiement` varchar(255) NOT NULL,
  `description` text DEFAULT NULL,
  `montant` decimal(10,2) NOT NULL,
  `type_reglement` varchar(50) NOT NULL,
  `banque` varchar(255) DEFAULT NULL,
  `numero_bon` int(11) NOT NULL,
  `numero_carnet` int(11) NOT NULL,
  `code_saison` varchar(10) NOT NULL,
  `date_paiement` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `autres_paiements`
--

INSERT INTO `autres_paiements` (`id`, `nom_paiement`, `description`, `montant`, `type_reglement`, `banque`, `numero_bon`, `numero_carnet`, `code_saison`, `date_paiement`) VALUES
(1, 'test', 'aaazaevczv', 100.00, 'espèce', NULL, 1, 1, 'S2025', '2025-08-25 12:52:45'),
(2, 'test2', 'aefdazef', 150.00, 'espèce', NULL, 2, 1, 'S2025', '2025-08-26 11:24:45');

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
-- Structure de la table `cotisations`
--

CREATE TABLE `cotisations` (
  `id_cotisation` int(11) NOT NULL,
  `nom_cotisation` varchar(100) NOT NULL,
  `montant_cotisation` float NOT NULL,
  `code_saison` varchar(10) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `cotisations`
--

INSERT INTO `cotisations` (`id_cotisation`, `nom_cotisation`, `montant_cotisation`, `code_saison`) VALUES
(12, 'Poussin-1-A', 1600, 'S2025'),
(13, 'Poussin-1-B', 1300, 'S2025'),
(14, 'Benjamin-1-A', 1900, 'S2025'),
(15, 'Benjamin-1-B', 1700, 'S2025'),
(16, 'KD-1-A', 2000, 'S2025'),
(17, 'KD-1-B', 1900, 'S2025'),
(18, 'Ecole-1-A', 1400, 'E2025'),
(19, 'Ecole d\'été-1-A', 900, 'E2025'),
(20, 'Lutin-1-A', 1650, 'S2025'),
(21, 'Lutin-1-B', 1600, 'S2025'),
(22, 'Minime-1-A', 1200, 'S2025'),
(23, 'Minime-1-B', 1200, 'S2025'),
(26, 'Adulte-5-A', 2000, 'S2025');

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

--
-- Déchargement des données de la table `depense`
--

INSERT INTO `depense` (`id`, `libelle`, `montant`, `date`, `type_depense`) VALUES
(8, 'test1', 100.00, '2025-08-26', 'A'),
(9, 'test2', 50.00, '2025-08-26', 'B');

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
  `status` enum('Actif','Non-Actif') NOT NULL,
  `tel` varchar(100) DEFAULT NULL,
  `addresse` varchar(100) DEFAULT NULL,
  `compte_bancaire` varchar(100) DEFAULT NULL,
  `code_saison` varchar(10) DEFAULT NULL,
  `role_technique` varchar(50) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `entraineur`
--

INSERT INTO `entraineur` (`id_entraineur`, `nom`, `prenom`, `sexe`, `type_abonnement`, `status`, `tel`, `addresse`, `compte_bancaire`, `code_saison`, `role_technique`) VALUES
(11, 'Zallila', 'Adam', 'M', 'Ecole', 'Actif', NULL, NULL, NULL, 'S2025', 'Entraineur'),
(12, 'Jaber', 'Ons', 'F', 'Loisir', 'Actif', '1234', 'rue x', '123456789', 'S2025', 'Entraineur'),
(13, 'Mhiri', 'Afif', 'M', 'Pré-Compétitif', 'Actif', '1234', 'x', '1234', 'S2025', 'Entraineur'),
(14, 'Jebri', 'Amine', 'M', 'Loisir', 'Actif', '1234', 'x', '1234', 'S2025', 'Entraineur'),
(15, 'Jegham', 'Anis', 'M', 'Adulte', 'Actif', '1234', 'x', '1234', 'S2025', 'Entraineur'),
(16, 'Hdaya', 'Aya', 'F', 'N/D', 'Actif', '1234', 'x', '1234', 'S2025', 'Entraineur'),
(17, 'Gaaloul', 'Ilhem', 'F', 'N/D', 'Actif', '1234', 'x', '1234', 'S2025', 'Entraineur'),
(18, 'Kbaili', 'Nour', 'F', 'N/D', 'Actif', '1234', 'x', '1234', 'S2025', 'Entraineur'),
(19, 'Kharrat', 'Ramzi', 'M', 'N/D', 'Actif', '1234', 'x', '1234', 'S2025', 'Entraineur'),
(20, 'Missoum', 'Walid', 'M', 'N/D', 'Actif', '1234', 'x', '1234', 'S2025', 'Entraineur'),
(21, 'mohamed', 'saleh', 'M', 'Loisir', 'Actif', '12345678', 'aaaaaa', '123456789', 'S2025', 'Entraineur'),
(22, 'Ali', 'Mohamed', 'M', 'prep_physique', 'Actif', '12345678', 'aaezefa', '1549864561', 'S2025', 'Prep Physique'),
(23, 'Ben Ali', 'Saleh', 'M', 'prep_physique', 'Actif', '12345678', 'zefvzvze', '54984651', 'S2025', 'Prep Physique');

-- --------------------------------------------------------

--
-- Structure de la table `groupe`
--

CREATE TABLE `groupe` (
  `id_groupe` int(11) NOT NULL,
  `nom_groupe` varchar(100) NOT NULL,
  `entraineur_nom` varchar(50) NOT NULL,
  `type_abonnement` varchar(50) NOT NULL,
  `categorie` varchar(50) NOT NULL,
  `preparateur_physique` varchar(100) DEFAULT NULL,
  `saison_code` varchar(10) DEFAULT NULL,
  `date_creation` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `groupe`
--

INSERT INTO `groupe` (`id_groupe`, `nom_groupe`, `entraineur_nom`, `type_abonnement`, `categorie`, `preparateur_physique`, `saison_code`, `date_creation`) VALUES
(7, 'Poussin-1-A', 'Zallila Adam', 'Compétitif', 'Poussin', 'Ben Ali Saleh', 'S2025', '2025-10-23 10:29:23'),
(8, 'Poussin-1-B', 'Zallila Adam', 'Compétitif', 'Poussin', NULL, 'S2025', '2025-10-23 10:29:23'),
(9, 'Lutin-1-A', 'Kharrat Ramzi', 'Loisir', 'Lutin', NULL, 'S2025', '2025-10-23 10:29:23'),
(10, 'Lutin-1-B', 'Kharrat Ramzi', 'Loisir', 'Lutin', NULL, 'S2025', '2025-10-23 10:29:23'),
(11, 'Benjamin-1-A', 'Missoum Walid', 'N/D', 'Benjamin', NULL, 'S2025', '2025-10-23 10:29:23'),
(12, 'Benjamin-1-B', 'Missoum Walid', 'N/D', 'Benjamin', NULL, 'S2025', '2025-10-23 10:29:23'),
(13, 'Minime-1-A', 'Gaaloul Ilhem', 'N/D', 'Minime', 'Ali Mohamed', 'S2025', '2025-10-23 10:29:23'),
(14, 'Minime-1-B', 'Gaaloul Ilhem', 'N/D', 'Minime', NULL, 'S2025', '2025-10-23 10:29:23'),
(15, 'KD-1-A', 'Hdaya Aya', 'N/D', 'KD', NULL, 'S2025', '2025-10-23 10:29:23'),
(16, 'KD-1-B', 'Hdaya Aya', 'N/D', 'KD', NULL, 'S2025', '2025-10-23 10:29:23'),
(21, 'Ecole d\'été-1-A', 'Hdaya Aya', 'N/D', 'Ecole d\'été', NULL, 'E2025', '2025-10-23 10:29:23'),
(24, 'Benjamin-1-C', 'Jebri Amine', 'N/D', 'Benjamin', 'Ben Ali Saleh', 'S2025', '2025-10-23 10:29:23'),
(25, 'Ecole_ete-2-A', 'Ali Mohamed', 'Loisir', 'Ecole_ete', 'Ben Ali Saleh', 'E2025', '2025-10-23 10:29:23'),
(26, 'Adulte-5-A', 'john doe', 'Loisir', 'Adulte', 'Ali Mohamed', 'S2025', '2025-10-23 09:32:34');

-- --------------------------------------------------------

--
-- Structure de la table `locations_terrains`
--

CREATE TABLE `locations_terrains` (
  `id_location` int(11) NOT NULL,
  `numero_terrain` int(11) NOT NULL,
  `heure_debut` time NOT NULL,
  `heure_fin` time NOT NULL,
  `date_location` date NOT NULL,
  `locateur` varchar(100) NOT NULL,
  `montant_location` float NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `locations_terrains`
--

INSERT INTO `locations_terrains` (`id_location`, `numero_terrain`, `heure_debut`, `heure_fin`, `date_location`, `locateur`, `montant_location`) VALUES
(3, 1, '08:00:00', '09:00:00', '2025-03-01', 'ahmed1', 100),
(4, 1, '09:00:00', '10:00:00', '2025-03-01', 'ahmed', 100),
(5, 2, '10:00:00', '12:00:00', '2025-03-01', 'x', 150);

-- --------------------------------------------------------

--
-- Structure de la table `match`
--

CREATE TABLE `match` (
  `id_match` int(11) NOT NULL,
  `id_tournoi` int(11) NOT NULL,
  `round` enum('poule','1/16','1/8','quart','demi','final') NOT NULL,
  `joueur1` int(11) DEFAULT NULL,
  `joueur2` int(11) DEFAULT NULL,
  `score_j1` int(11) DEFAULT NULL,
  `score_j2` int(11) DEFAULT NULL,
  `gagnant` int(11) DEFAULT NULL,
  `match_suivant` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

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
(9, 'admin', '', 'hello', 'hello', '2025-01-21 07:08:03', 'non lu'),
(10, 'jaber.ons', '', 'Test', 'Bonjour', '2025-01-22 14:43:05', 'non lu'),
(11, 'mhiri.afif', 'manager', 'absence', 'bonjour,\r\nje veux vous informer que je ne serais pas disponible pour le lundi 20/01/2025.\r\nMerci', '2025-01-24 20:10:27', 'non lu'),
(12, 'manager', 'mhiri.afif', 'Reponse Absence', 'Ok bien recu.', '2025-01-24 20:13:32', 'non lu'),
(13, 'Zallila.Adam', 'admin,manager', 'hello', 'hello', '2025-01-28 07:40:34', 'non lu');

-- --------------------------------------------------------

--
-- Structure de la table `paiements`
--

CREATE TABLE `paiements` (
  `id_paiement` int(11) NOT NULL,
  `matricule_adherent` varchar(20) NOT NULL,
  `numero_bon` int(11) NOT NULL,
  `numero_carnet` int(11) NOT NULL,
  `date_paiement` datetime NOT NULL DEFAULT current_timestamp(),
  `montant` decimal(10,2) NOT NULL,
  `total_montant_paye` float NOT NULL DEFAULT 0,
  `montant_paye` decimal(10,2) NOT NULL DEFAULT 0.00,
  `montant_reste` decimal(10,2) NOT NULL,
  `type_reglement` varchar(50) DEFAULT NULL,
  `numero_cheque` varchar(50) DEFAULT NULL,
  `banque` varchar(50) DEFAULT NULL,
  `cotisation` decimal(10,2) NOT NULL,
  `remise` decimal(10,2) NOT NULL DEFAULT 0.00,
  `code_saison` varchar(50) NOT NULL,
  `etat` varchar(20) NOT NULL DEFAULT 'actif',
  `date_annulation` datetime DEFAULT NULL,
  `annule_par` varchar(100) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `paiements`
--

INSERT INTO `paiements` (`id_paiement`, `matricule_adherent`, `numero_bon`, `numero_carnet`, `date_paiement`, `montant`, `total_montant_paye`, `montant_paye`, `montant_reste`, `type_reglement`, `numero_cheque`, `banque`, `cotisation`, `remise`, `code_saison`, `etat`, `date_annulation`, `annule_par`) VALUES
(25, '2', 1, 1, '2025-01-28 16:19:40', 450.00, 300, 300.00, 150.00, 'chèque', '123456789', 'BIAT', 500.00, 10.00, 'S2025', 'actif', NULL, NULL),
(26, '2', 2, 1, '2025-01-28 16:40:44', 450.00, 100, 100.00, 350.00, 'chèque', '123486', 'x', 500.00, 10.00, 'S2025', 'actif', NULL, NULL),
(27, '1', 3, 1, '2025-01-29 16:36:56', 665.00, 500, 500.00, 165.00, 'chèque', '123456789', 'x', 700.00, 5.00, 'S2025', 'actif', NULL, NULL),
(28, '2', 4, 1, '2025-01-29 17:46:49', 450.00, 50, 50.00, 400.00, 'espèce', NULL, NULL, 500.00, 10.00, 'S2025', 'actif', NULL, NULL),
(29, '5', 5, 1, '2025-02-07 08:20:21', 450.00, 200, 200.00, 250.00, 'espèce', NULL, NULL, 500.00, 10.00, 'S2025', 'annule', '2025-10-28 11:35:03', 'admin'),
(30, '4', 6, 1, '2025-02-07 09:34:14', 540.00, 300, 300.00, 240.00, 'espèce', NULL, NULL, 600.00, 10.00, 'S2025', 'actif', NULL, NULL),
(31, '6', 7, 1, '2025-02-07 09:39:08', 250.00, 100, 100.00, 150.00, 'espèce', NULL, NULL, 250.00, 0.00, 'S2025', 'actif', NULL, NULL),
(32, '1', 8, 1, '2025-02-09 13:48:50', 665.00, 165, 165.00, 500.00, 'espèce', NULL, NULL, 700.00, 5.00, 'S2025', 'actif', NULL, NULL),
(33, '3', 9, 1, '2025-08-25 10:40:33', 200.00, 100, 100.00, 100.00, 'espèce', NULL, NULL, 200.00, 0.00, 'S2025', 'actif', NULL, NULL),
(34, '3', 10, 1, '2025-08-25 10:40:43', 200.00, 200, 100.00, 0.00, 'espèce', NULL, NULL, 200.00, 0.00, 'S2025', 'actif', NULL, NULL),
(35, '12', 11, 1, '2025-08-26 13:07:52', 1600.00, 0, 0.00, 1600.00, 'espèce', NULL, NULL, 1600.00, 0.00, 'S2025', 'actif', NULL, NULL),
(36, '13', 12, 1, '2025-08-28 12:36:52', 1100.00, 100, 100.00, 1000.00, 'espèce', NULL, NULL, 1100.00, 0.00, 'S2025', 'actif', NULL, NULL),
(37, '13', 13, 1, '2025-08-28 12:45:52', 1100.00, 200, 100.00, 900.00, 'espèce', NULL, NULL, 1100.00, 0.00, 'S2025', 'actif', NULL, NULL),
(39, '13', 14, 1, '2025-08-28 12:54:18', 1100.00, 1100, 900.00, 0.00, 'espèce', NULL, NULL, 1100.00, 0.00, 'S2025', 'actif', NULL, NULL),
(40, '11', 15, 1, '2025-09-09 09:47:07', 1350.00, 200, 200.00, 1150.00, 'espèce', NULL, NULL, 1500.00, 10.00, 'E2025', 'actif', NULL, NULL),
(41, '16', 16, 1, '2025-09-09 16:57:51', 1440.00, 100, 100.00, 1340.00, 'espèce', NULL, NULL, 1440.00, 10.00, 'S2025', 'actif', NULL, NULL),
(42, '16', 17, 1, '2025-09-09 17:02:09', 1440.00, 200, 100.00, 1240.00, 'espèce', NULL, NULL, 1440.00, 10.00, 'S2025', 'actif', NULL, NULL),
(43, '18', 18, 1, '2025-09-23 13:04:55', 1200.00, 100, 100.00, 1100.00, 'espèce', NULL, NULL, 1200.00, 5.00, 'S2025', 'actif', NULL, NULL),
(44, '10', 19, 1, '2025-10-28 09:44:52', 1200.00, 0, 500.00, 700.00, 'espèce', '', '', 1200.00, 0.00, 'S2025', 'actif', NULL, NULL),
(45, '10', 19, 1, '2025-10-28 09:44:52', 1200.00, 0, 500.00, 700.00, 'espèce', '', '', 1200.00, 0.00, 'S2025', 'annule', '2025-10-28 11:30:21', 'admin'),
(46, '10', 19, 1, '2025-10-28 09:44:52', 1200.00, 0, 500.00, 700.00, 'espèce', '', '', 1200.00, 0.00, 'S2025', 'annule', '2025-10-28 11:30:19', 'admin'),
(47, '10', 19, 1, '2025-10-28 09:44:52', 1200.00, 0, 500.00, 700.00, 'espèce', '', '', 1200.00, 0.00, 'S2025', 'annule', '2025-10-28 11:29:59', 'admin'),
(48, '13', 20, 1, '2025-10-28 11:38:31', 1300.00, 0, 100.00, 100.00, 'espèce', '', '', 1300.00, 0.00, 'S2025', 'annule', '2025-10-28 11:38:42', 'admin'),
(49, '10', 21, 1, '2025-10-28 12:12:41', 1200.00, 0, 100.00, 600.00, 'espèce', '', '', 1200.00, 0.00, 'S2025', 'actif', NULL, NULL);

-- --------------------------------------------------------

--
-- Structure de la table `participanttournoi`
--

CREATE TABLE `participanttournoi` (
  `id_participation` int(11) NOT NULL,
  `id_utilisateur` int(11) NOT NULL,
  `id_tournoi` int(11) NOT NULL,
  `poule` int(11) NOT NULL,
  `points` int(11) DEFAULT 0,
  `position_finale` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Structure de la table `presence`
--

CREATE TABLE `presence` (
  `id_presence` int(11) NOT NULL,
  `groupe_nom` varchar(100) NOT NULL,
  `adherent_matricule` text DEFAULT NULL,
  `entraineur_nom` varchar(100) NOT NULL,
  `date_seance` date NOT NULL,
  `heure_debut` time NOT NULL,
  `est_present` enum('O','N') NOT NULL DEFAULT 'N',
  `seance_id` int(11) DEFAULT NULL,
  `seance_type` enum('entrainement','prep_physique') NOT NULL DEFAULT 'entrainement'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `presence`
--

INSERT INTO `presence` (`id_presence`, `groupe_nom`, `adherent_matricule`, `entraineur_nom`, `date_seance`, `heure_debut`, `est_present`, `seance_id`, `seance_type`) VALUES
(1, 'loisir', '4', 'john doe', '2025-01-23', '10:30:00', 'O', NULL, 'entrainement'),
(2, 'loisir', '4', 'john doe', '2025-01-22', '10:30:00', 'N', NULL, 'entrainement'),
(3, 'groupe_onsjaber', '8', 'Jaber Ons', '2025-01-22', '16:30:00', 'O', NULL, 'entrainement'),
(4, 'groupe_onsjaber', '8', 'Jaber Ons', '2025-01-20', '16:30:00', 'N', NULL, 'entrainement'),
(5, 'Ecole d\'été-1-A', '10', 'Zallila Adam', '2025-08-26', '08:00:00', 'O', 34, 'entrainement'),
(12, 'Poussin-1-B', '7,17', 'Zallila Adam', '2025-09-23', '10:00:00', 'O', 396, 'prep_physique'),
(13, 'Poussin-1-B', '7,17', 'Zallila Adam', '2025-09-22', '09:30:00', 'O', 141, 'entrainement');

-- --------------------------------------------------------

--
-- Structure de la table `presence_entraineurs`
--

CREATE TABLE `presence_entraineurs` (
  `id_presence` int(11) NOT NULL,
  `entraineur_nom` varchar(100) NOT NULL,
  `seance_id` int(11) NOT NULL,
  `date_seance` date NOT NULL,
  `heure_debut` time NOT NULL,
  `est_present` enum('O','N') NOT NULL DEFAULT 'N',
  `commentaire` text DEFAULT NULL,
  `date_creation` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `presence_entraineurs`
--

INSERT INTO `presence_entraineurs` (`id_presence`, `entraineur_nom`, `seance_id`, `date_seance`, `heure_debut`, `est_present`, `commentaire`, `date_creation`) VALUES
(7, 'Zallila Adam', 396, '2025-09-23', '10:00:00', 'O', 'prep_physique', '2025-09-24 09:05:59'),
(8, 'Zallila Adam', 141, '2025-09-22', '09:30:00', 'O', 'entrainement', '2025-09-24 09:17:49');

-- --------------------------------------------------------

--
-- Structure de la table `reservations`
--

CREATE TABLE `reservations` (
  `id_reservation` int(11) NOT NULL,
  `nom_entraineur` varchar(100) NOT NULL,
  `prenom_entraineur` varchar(100) NOT NULL,
  `date_reservation` date NOT NULL,
  `heure_debut` time NOT NULL,
  `heure_fin` time NOT NULL,
  `numero_terrain` int(11) NOT NULL,
  `commentaire` text DEFAULT NULL,
  `status` enum('en_attente','acceptée','refusée') DEFAULT 'en_attente',
  `date_creation` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `reservations`
--

INSERT INTO `reservations` (`id_reservation`, `nom_entraineur`, `prenom_entraineur`, `date_reservation`, `heure_debut`, `heure_fin`, `numero_terrain`, `commentaire`, `status`, `date_creation`) VALUES
(1, 'Zallila', 'Adam', '2025-08-26', '15:00:00', '17:00:00', 1, 'test', 'en_attente', '2025-08-26 09:20:08');

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
  `heure_debut` time NOT NULL,
  `heure_fin` time NOT NULL,
  `groupe` varchar(100) NOT NULL,
  `entraineur` varchar(100) NOT NULL,
  `terrain` int(11) DEFAULT NULL,
  `adherents_matricules` text DEFAULT NULL,
  `type_seance` varchar(50) NOT NULL DEFAULT 'entrainement',
  `duree` int(11) DEFAULT NULL,
  `code_saison` varchar(10) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `seances`
--

INSERT INTO `seances` (`seance_id`, `date`, `heure_debut`, `heure_fin`, `groupe`, `entraineur`, `terrain`, `adherents_matricules`, `type_seance`, `duree`, `code_saison`) VALUES
(6, '2025-01-29', '12:30:00', '14:00:00', 'Poussin-1-B', 'Kharrat Ramzi', 2, NULL, 'entrainement', 90, 'S2025'),
(10, '2025-01-16', '11:00:00', '12:30:00', 'Lutin-1-A', 'Kharrat Ramzi', 3, NULL, 'entrainement', 90, 'S2025'),
(15, '2025-01-23', '08:00:00', '09:30:00', 'Lutin-1-A', 'Kharrat Ramzi', 1, NULL, 'entrainement', 90, 'S2025'),
(17, '2025-01-20', '08:00:00', '09:30:00', 'Poussin-1-A', 'Hdaya Aya', 2, NULL, 'entrainement', 90, 'S2025'),
(19, '2025-01-28', '08:00:00', '09:30:00', 'Lutin-1-A', 'Kharrat Ramzi', 1, NULL, 'entrainement', 90, 'S2025'),
(20, '2025-01-28', '09:30:00', '11:00:00', 'Lutin-1-A', 'Kharrat Ramzi', 1, NULL, 'entrainement', 90, 'S2025'),
(21, '2025-02-03', '09:30:00', '11:00:00', 'Lutin-1-B', 'Kharrat Ramzi', 1, NULL, 'entrainement', 90, 'S2025'),
(22, '2025-01-20', '09:30:00', '11:00:00', 'Poussin-1-B', 'Hdaya Aya', 2, NULL, 'entrainement', 90, 'S2025'),
(23, '2025-01-21', '08:00:00', '09:30:00', 'Poussin-1-B', 'Hdaya Aya', 1, NULL, 'entrainement', 90, 'S2025'),
(25, '2025-01-20', '09:30:00', '11:00:00', 'Lutin-1-A', 'Kharrat Ramzi', 1, NULL, 'entrainement', 90, 'S2025'),
(29, '2025-01-27', '08:00:00', '09:30:00', 'Poussin-1-B', 'Hdaya Aya', 1, NULL, 'entrainement', 90, 'S2025'),
(32, '2025-02-03', '12:30:00', '14:00:00', 'Poussin-1-A', 'Hdaya Aya', 1, NULL, 'entrainement', 90, 'S2025'),
(34, '2025-09-23', '08:00:00', '09:30:00', 'Ecole d\'été-1-A', 'Hdaya Aya', 1, NULL, 'entrainement', 90, 'S2025'),
(139, '2025-09-08', '09:30:00', '11:00:00', 'Poussin-1-B', 'Zallila Adam', 1, NULL, 'entrainement', 90, 'S2025'),
(140, '2025-09-15', '09:30:00', '11:00:00', 'Poussin-1-B', 'Zallila Adam', 1, NULL, 'entrainement', 90, 'S2025'),
(141, '2025-09-22', '09:30:00', '11:00:00', 'Poussin-1-B', 'Zallila Adam', 1, NULL, 'entrainement', 90, 'S2025'),
(142, '2025-09-29', '09:30:00', '11:00:00', 'Poussin-1-B', 'Zallila Adam', 1, NULL, 'entrainement', 90, 'S2025'),
(143, '2025-10-06', '09:30:00', '11:00:00', 'Poussin-1-B', 'Zallila Adam', 1, NULL, 'entrainement', 90, 'S2025'),
(144, '2025-10-13', '09:30:00', '11:00:00', 'Poussin-1-B', 'Zallila Adam', 1, NULL, 'entrainement', 90, 'S2025'),
(145, '2025-10-20', '09:30:00', '11:00:00', 'Poussin-1-B', 'Zallila Adam', 1, NULL, 'entrainement', 90, 'S2025'),
(146, '2025-10-27', '09:30:00', '11:00:00', 'Poussin-1-B', 'Zallila Adam', 1, NULL, 'entrainement', 90, 'S2025'),
(147, '2025-11-03', '09:30:00', '11:00:00', 'Poussin-1-B', 'Zallila Adam', 1, NULL, 'entrainement', 90, 'S2025'),
(148, '2025-11-10', '09:30:00', '11:00:00', 'Poussin-1-B', 'Zallila Adam', 1, NULL, 'entrainement', 90, 'S2025'),
(149, '2025-11-17', '09:30:00', '11:00:00', 'Poussin-1-B', 'Zallila Adam', 1, NULL, 'entrainement', 90, 'S2025'),
(150, '2025-11-24', '09:30:00', '11:00:00', 'Poussin-1-B', 'Zallila Adam', 1, NULL, 'entrainement', 90, 'S2025'),
(151, '2025-12-01', '09:30:00', '11:00:00', 'Poussin-1-B', 'Zallila Adam', 1, NULL, 'entrainement', 90, 'S2025'),
(152, '2025-12-08', '09:30:00', '11:00:00', 'Poussin-1-B', 'Zallila Adam', 1, NULL, 'entrainement', 90, 'S2025'),
(153, '2025-12-15', '09:30:00', '11:00:00', 'Poussin-1-B', 'Zallila Adam', 1, NULL, 'entrainement', 90, 'S2025'),
(154, '2025-12-22', '09:30:00', '11:00:00', 'Poussin-1-B', 'Zallila Adam', 1, NULL, 'entrainement', 90, 'S2025'),
(155, '2025-12-29', '09:30:00', '11:00:00', 'Poussin-1-B', 'Zallila Adam', 1, NULL, 'entrainement', 90, 'S2025'),
(156, '2026-01-05', '09:30:00', '11:00:00', 'Poussin-1-B', 'Zallila Adam', 1, NULL, 'entrainement', 90, 'S2025'),
(157, '2026-01-12', '09:30:00', '11:00:00', 'Poussin-1-B', 'Zallila Adam', 1, NULL, 'entrainement', 90, 'S2025'),
(158, '2026-01-19', '09:30:00', '11:00:00', 'Poussin-1-B', 'Zallila Adam', 1, NULL, 'entrainement', 90, 'S2025'),
(159, '2026-01-26', '09:30:00', '11:00:00', 'Poussin-1-B', 'Zallila Adam', 1, NULL, 'entrainement', 90, 'S2025'),
(160, '2026-02-02', '09:30:00', '11:00:00', 'Poussin-1-B', 'Zallila Adam', 1, NULL, 'entrainement', 90, 'S2025'),
(161, '2026-02-09', '09:30:00', '11:00:00', 'Poussin-1-B', 'Zallila Adam', 1, NULL, 'entrainement', 90, 'S2025'),
(162, '2026-02-16', '09:30:00', '11:00:00', 'Poussin-1-B', 'Zallila Adam', 1, NULL, 'entrainement', 90, 'S2025'),
(163, '2026-02-23', '09:30:00', '11:00:00', 'Poussin-1-B', 'Zallila Adam', 1, NULL, 'entrainement', 90, 'S2025'),
(164, '2026-03-02', '09:30:00', '11:00:00', 'Poussin-1-B', 'Zallila Adam', 1, NULL, 'entrainement', 90, 'S2025'),
(165, '2026-03-09', '09:30:00', '11:00:00', 'Poussin-1-B', 'Zallila Adam', 1, NULL, 'entrainement', 90, 'S2025'),
(166, '2026-03-16', '09:30:00', '11:00:00', 'Poussin-1-B', 'Zallila Adam', 1, NULL, 'entrainement', 90, 'S2025'),
(167, '2026-03-23', '09:30:00', '11:00:00', 'Poussin-1-B', 'Zallila Adam', 1, NULL, 'entrainement', 90, 'S2025'),
(168, '2026-03-30', '09:30:00', '11:00:00', 'Poussin-1-B', 'Zallila Adam', 1, NULL, 'entrainement', 90, 'S2025'),
(169, '2026-04-06', '09:30:00', '11:00:00', 'Poussin-1-B', 'Zallila Adam', 1, NULL, 'entrainement', 90, 'S2025'),
(170, '2026-04-13', '09:30:00', '11:00:00', 'Poussin-1-B', 'Zallila Adam', 1, NULL, 'entrainement', 90, 'S2025'),
(171, '2026-04-20', '09:30:00', '11:00:00', 'Poussin-1-B', 'Zallila Adam', 1, NULL, 'entrainement', 90, 'S2025'),
(172, '2026-04-27', '09:30:00', '11:00:00', 'Poussin-1-B', 'Zallila Adam', 1, NULL, 'entrainement', 90, 'S2025'),
(173, '2026-05-04', '09:30:00', '11:00:00', 'Poussin-1-B', 'Zallila Adam', 1, NULL, 'entrainement', 90, 'S2025'),
(174, '2026-05-11', '09:30:00', '11:00:00', 'Poussin-1-B', 'Zallila Adam', 1, NULL, 'entrainement', 90, 'S2025'),
(175, '2026-05-18', '09:30:00', '11:00:00', 'Poussin-1-B', 'Zallila Adam', 1, NULL, 'entrainement', 90, 'S2025'),
(176, '2026-05-25', '09:30:00', '11:00:00', 'Poussin-1-B', 'Zallila Adam', 1, NULL, 'entrainement', 90, 'S2025'),
(177, '2026-06-01', '09:30:00', '11:00:00', 'Poussin-1-B', 'Zallila Adam', 1, NULL, 'entrainement', 90, 'S2025'),
(178, '2026-06-08', '09:30:00', '11:00:00', 'Poussin-1-B', 'Zallila Adam', 1, NULL, 'entrainement', 90, 'S2025'),
(179, '2026-06-15', '09:30:00', '11:00:00', 'Poussin-1-B', 'Zallila Adam', 1, NULL, 'entrainement', 90, 'S2025'),
(180, '2026-06-22', '09:30:00', '11:00:00', 'Poussin-1-B', 'Zallila Adam', 1, NULL, 'entrainement', 90, 'S2025'),
(181, '2026-06-29', '09:30:00', '11:00:00', 'Poussin-1-B', 'Zallila Adam', 1, NULL, 'entrainement', 90, 'S2025'),
(182, '2026-07-06', '09:30:00', '11:00:00', 'Poussin-1-B', 'Zallila Adam', 1, NULL, 'entrainement', 90, 'S2025'),
(183, '2026-07-13', '09:30:00', '11:00:00', 'Poussin-1-B', 'Zallila Adam', 1, NULL, 'entrainement', 90, 'S2025'),
(184, '2026-07-20', '09:30:00', '11:00:00', 'Poussin-1-B', 'Zallila Adam', 1, NULL, 'entrainement', 90, 'S2025'),
(185, '2026-07-27', '09:30:00', '11:00:00', 'Poussin-1-B', 'Zallila Adam', 1, NULL, 'entrainement', 90, 'S2025'),
(186, '2026-08-03', '09:30:00', '11:00:00', 'Poussin-1-B', 'Zallila Adam', 1, NULL, 'entrainement', 90, 'S2025'),
(187, '2026-08-10', '09:30:00', '11:00:00', 'Poussin-1-B', 'Zallila Adam', 1, NULL, 'entrainement', 90, 'S2025'),
(188, '2026-08-17', '09:30:00', '11:00:00', 'Poussin-1-B', 'Zallila Adam', 1, NULL, 'entrainement', 90, 'S2025'),
(189, '2026-08-24', '09:30:00', '11:00:00', 'Poussin-1-B', 'Zallila Adam', 1, NULL, 'entrainement', 90, 'S2025'),
(190, '2026-08-31', '09:30:00', '11:00:00', 'Poussin-1-B', 'Zallila Adam', 1, NULL, 'entrainement', 90, 'S2025'),
(192, '2025-09-09', '08:00:00', '09:30:00', 'Ecole d\'été-1-A', 'Hdaya Aya', 1, NULL, 'entrainement', 90, 'S2025'),
(193, '2025-09-11', '18:30:00', '20:00:00', 'Benjamin-1-C', 'Jebri Amine', 5, NULL, 'entrainement', 90, 'S2025'),
(194, '2025-09-18', '17:00:00', '18:30:00', 'Benjamin-1-C', 'Jebri Amine', 8, NULL, 'entrainement', 90, 'S2025'),
(195, '2025-09-25', '18:30:00', '20:00:00', 'Benjamin-1-C', 'Jebri Amine', 5, NULL, 'entrainement', 90, 'S2025'),
(196, '2025-10-02', '18:30:00', '20:00:00', 'Benjamin-1-C', 'Jebri Amine', 5, NULL, 'entrainement', 90, 'S2025'),
(197, '2025-10-09', '18:30:00', '20:00:00', 'Benjamin-1-C', 'Jebri Amine', 5, NULL, 'entrainement', 90, 'S2025'),
(198, '2025-10-16', '18:30:00', '20:00:00', 'Benjamin-1-C', 'Jebri Amine', 5, NULL, 'entrainement', 90, 'S2025'),
(199, '2025-10-23', '18:30:00', '20:00:00', 'Benjamin-1-C', 'Jebri Amine', 5, NULL, 'entrainement', 90, 'S2025'),
(200, '2025-10-30', '18:30:00', '20:00:00', 'Benjamin-1-C', 'Jebri Amine', 5, NULL, 'entrainement', 90, 'S2025'),
(201, '2025-11-06', '18:30:00', '20:00:00', 'Benjamin-1-C', 'Jebri Amine', 5, NULL, 'entrainement', 90, 'S2025'),
(202, '2025-11-13', '18:30:00', '20:00:00', 'Benjamin-1-C', 'Jebri Amine', 5, NULL, 'entrainement', 90, 'S2025'),
(203, '2025-11-20', '18:30:00', '20:00:00', 'Benjamin-1-C', 'Jebri Amine', 5, NULL, 'entrainement', 90, 'S2025'),
(204, '2025-11-27', '18:30:00', '20:00:00', 'Benjamin-1-C', 'Jebri Amine', 5, NULL, 'entrainement', 90, 'S2025'),
(205, '2025-12-04', '18:30:00', '20:00:00', 'Benjamin-1-C', 'Jebri Amine', 5, NULL, 'entrainement', 90, 'S2025'),
(206, '2025-12-11', '18:30:00', '20:00:00', 'Benjamin-1-C', 'Jebri Amine', 5, NULL, 'entrainement', 90, 'S2025'),
(207, '2025-12-18', '18:30:00', '20:00:00', 'Benjamin-1-C', 'Jebri Amine', 5, NULL, 'entrainement', 90, 'S2025'),
(208, '2025-12-25', '18:30:00', '20:00:00', 'Benjamin-1-C', 'Jebri Amine', 5, NULL, 'entrainement', 90, 'S2025'),
(209, '2026-01-01', '18:30:00', '20:00:00', 'Benjamin-1-C', 'Jebri Amine', 5, NULL, 'entrainement', 90, 'S2025'),
(210, '2026-01-08', '18:30:00', '20:00:00', 'Benjamin-1-C', 'Jebri Amine', 5, NULL, 'entrainement', 90, 'S2025'),
(211, '2026-01-15', '18:30:00', '20:00:00', 'Benjamin-1-C', 'Jebri Amine', 5, NULL, 'entrainement', 90, 'S2025'),
(212, '2026-01-22', '18:30:00', '20:00:00', 'Benjamin-1-C', 'Jebri Amine', 5, NULL, 'entrainement', 90, 'S2025'),
(213, '2026-01-29', '18:30:00', '20:00:00', 'Benjamin-1-C', 'Jebri Amine', 5, NULL, 'entrainement', 90, 'S2025'),
(214, '2026-02-05', '18:30:00', '20:00:00', 'Benjamin-1-C', 'Jebri Amine', 5, NULL, 'entrainement', 90, 'S2025'),
(215, '2026-02-12', '18:30:00', '20:00:00', 'Benjamin-1-C', 'Jebri Amine', 5, NULL, 'entrainement', 90, 'S2025'),
(216, '2026-02-19', '18:30:00', '20:00:00', 'Benjamin-1-C', 'Jebri Amine', 5, NULL, 'entrainement', 90, 'S2025'),
(217, '2026-02-26', '18:30:00', '20:00:00', 'Benjamin-1-C', 'Jebri Amine', 5, NULL, 'entrainement', 90, 'S2025'),
(218, '2026-03-05', '18:30:00', '20:00:00', 'Benjamin-1-C', 'Jebri Amine', 5, NULL, 'entrainement', 90, 'S2025'),
(219, '2026-03-12', '18:30:00', '20:00:00', 'Benjamin-1-C', 'Jebri Amine', 5, NULL, 'entrainement', 90, 'S2025'),
(220, '2026-03-19', '18:30:00', '20:00:00', 'Benjamin-1-C', 'Jebri Amine', 5, NULL, 'entrainement', 90, 'S2025'),
(221, '2026-03-26', '18:30:00', '20:00:00', 'Benjamin-1-C', 'Jebri Amine', 5, NULL, 'entrainement', 90, 'S2025'),
(222, '2026-04-02', '18:30:00', '20:00:00', 'Benjamin-1-C', 'Jebri Amine', 5, NULL, 'entrainement', 90, 'S2025'),
(223, '2026-04-09', '18:30:00', '20:00:00', 'Benjamin-1-C', 'Jebri Amine', 5, NULL, 'entrainement', 90, 'S2025'),
(224, '2026-04-16', '18:30:00', '20:00:00', 'Benjamin-1-C', 'Jebri Amine', 5, NULL, 'entrainement', 90, 'S2025'),
(225, '2026-04-23', '18:30:00', '20:00:00', 'Benjamin-1-C', 'Jebri Amine', 5, NULL, 'entrainement', 90, 'S2025'),
(226, '2026-04-30', '18:30:00', '20:00:00', 'Benjamin-1-C', 'Jebri Amine', 5, NULL, 'entrainement', 90, 'S2025'),
(227, '2026-05-07', '18:30:00', '20:00:00', 'Benjamin-1-C', 'Jebri Amine', 5, NULL, 'entrainement', 90, 'S2025'),
(228, '2026-05-14', '18:30:00', '20:00:00', 'Benjamin-1-C', 'Jebri Amine', 5, NULL, 'entrainement', 90, 'S2025'),
(229, '2026-05-21', '18:30:00', '20:00:00', 'Benjamin-1-C', 'Jebri Amine', 5, NULL, 'entrainement', 90, 'S2025'),
(230, '2026-05-28', '18:30:00', '20:00:00', 'Benjamin-1-C', 'Jebri Amine', 5, NULL, 'entrainement', 90, 'S2025'),
(231, '2026-06-04', '18:30:00', '20:00:00', 'Benjamin-1-C', 'Jebri Amine', 5, NULL, 'entrainement', 90, 'S2025'),
(232, '2026-06-11', '18:30:00', '20:00:00', 'Benjamin-1-C', 'Jebri Amine', 5, NULL, 'entrainement', 90, 'S2025'),
(233, '2026-06-18', '18:30:00', '20:00:00', 'Benjamin-1-C', 'Jebri Amine', 5, NULL, 'entrainement', 90, 'S2025'),
(234, '2026-06-25', '18:30:00', '20:00:00', 'Benjamin-1-C', 'Jebri Amine', 5, NULL, 'entrainement', 90, 'S2025'),
(235, '2026-07-02', '18:30:00', '20:00:00', 'Benjamin-1-C', 'Jebri Amine', 5, NULL, 'entrainement', 90, 'S2025'),
(236, '2026-07-09', '18:30:00', '20:00:00', 'Benjamin-1-C', 'Jebri Amine', 5, NULL, 'entrainement', 90, 'S2025'),
(237, '2026-07-16', '18:30:00', '20:00:00', 'Benjamin-1-C', 'Jebri Amine', 5, NULL, 'entrainement', 90, 'S2025'),
(238, '2026-07-23', '18:30:00', '20:00:00', 'Benjamin-1-C', 'Jebri Amine', 5, NULL, 'entrainement', 90, 'S2025'),
(239, '2026-07-30', '18:30:00', '20:00:00', 'Benjamin-1-C', 'Jebri Amine', 5, NULL, 'entrainement', 90, 'S2025'),
(240, '2026-08-06', '18:30:00', '20:00:00', 'Benjamin-1-C', 'Jebri Amine', 5, NULL, 'entrainement', 90, 'S2025'),
(241, '2026-08-13', '18:30:00', '20:00:00', 'Benjamin-1-C', 'Jebri Amine', 5, NULL, 'entrainement', 90, 'S2025'),
(242, '2026-08-20', '18:30:00', '20:00:00', 'Benjamin-1-C', 'Jebri Amine', 5, NULL, 'entrainement', 90, 'S2025'),
(243, '2026-08-27', '18:30:00', '20:00:00', 'Benjamin-1-C', 'Jebri Amine', 5, NULL, 'entrainement', 90, 'S2025'),
(295, '2025-09-16', '08:00:00', '09:00:00', 'Poussin-1-A', 'Mhiri Afif', 1, NULL, 'prep_physique', 60, 'S2025'),
(296, '2025-09-17', '08:00:00', '09:00:00', 'Lutin-1-A', 'Kharrat Ramzi', 0, NULL, 'prep_physique', 60, 'S2025'),
(297, '2025-09-17', '09:30:00', '11:00:00', 'Poussin-1-A', 'Mhiri Afif', 0, NULL, 'entrainement', 90, 'S2025'),
(298, '2025-09-23', '08:00:00', '09:30:00', 'Poussin-1-A', 'Mhiri Afif', 0, NULL, 'entrainement', 90, 'S2025'),
(299, '2025-09-30', '08:00:00', '09:30:00', 'Poussin-1-A', 'Mhiri Afif', 0, NULL, 'entrainement', 90, 'S2025'),
(300, '2025-10-07', '08:00:00', '09:30:00', 'Poussin-1-A', 'Mhiri Afif', 0, NULL, 'entrainement', 90, 'S2025'),
(301, '2025-10-14', '08:00:00', '09:30:00', 'Poussin-1-A', 'Mhiri Afif', 0, NULL, 'entrainement', 90, 'S2025'),
(302, '2025-10-21', '08:00:00', '09:30:00', 'Poussin-1-A', 'Mhiri Afif', 0, NULL, 'entrainement', 90, 'S2025'),
(303, '2025-10-28', '08:00:00', '09:30:00', 'Poussin-1-A', 'Mhiri Afif', 0, NULL, 'entrainement', 90, 'S2025'),
(304, '2025-11-04', '08:00:00', '09:30:00', 'Poussin-1-A', 'Mhiri Afif', 0, NULL, 'entrainement', 90, 'S2025'),
(305, '2025-11-11', '08:00:00', '09:30:00', 'Poussin-1-A', 'Mhiri Afif', 0, NULL, 'entrainement', 90, 'S2025'),
(306, '2025-11-18', '08:00:00', '09:30:00', 'Poussin-1-A', 'Mhiri Afif', 0, NULL, 'entrainement', 90, 'S2025'),
(307, '2025-11-25', '08:00:00', '09:30:00', 'Poussin-1-A', 'Mhiri Afif', 0, NULL, 'entrainement', 90, 'S2025'),
(308, '2025-12-02', '08:00:00', '09:30:00', 'Poussin-1-A', 'Mhiri Afif', 0, NULL, 'entrainement', 90, 'S2025'),
(309, '2025-12-09', '08:00:00', '09:30:00', 'Poussin-1-A', 'Mhiri Afif', 0, NULL, 'entrainement', 90, 'S2025'),
(310, '2025-12-16', '08:00:00', '09:30:00', 'Poussin-1-A', 'Mhiri Afif', 0, NULL, 'entrainement', 90, 'S2025'),
(311, '2025-12-23', '08:00:00', '09:30:00', 'Poussin-1-A', 'Mhiri Afif', 0, NULL, 'entrainement', 90, 'S2025'),
(312, '2025-12-30', '08:00:00', '09:30:00', 'Poussin-1-A', 'Mhiri Afif', 0, NULL, 'entrainement', 90, 'S2025'),
(313, '2026-01-06', '08:00:00', '09:30:00', 'Poussin-1-A', 'Mhiri Afif', 0, NULL, 'entrainement', 90, 'S2025'),
(314, '2026-01-13', '08:00:00', '09:30:00', 'Poussin-1-A', 'Mhiri Afif', 0, NULL, 'entrainement', 90, 'S2025'),
(315, '2026-01-20', '08:00:00', '09:30:00', 'Poussin-1-A', 'Mhiri Afif', 0, NULL, 'entrainement', 90, 'S2025'),
(316, '2026-01-27', '08:00:00', '09:30:00', 'Poussin-1-A', 'Mhiri Afif', 0, NULL, 'entrainement', 90, 'S2025'),
(317, '2026-02-03', '08:00:00', '09:30:00', 'Poussin-1-A', 'Mhiri Afif', 0, NULL, 'entrainement', 90, 'S2025'),
(318, '2026-02-10', '08:00:00', '09:30:00', 'Poussin-1-A', 'Mhiri Afif', 0, NULL, 'entrainement', 90, 'S2025'),
(319, '2026-02-17', '08:00:00', '09:30:00', 'Poussin-1-A', 'Mhiri Afif', 0, NULL, 'entrainement', 90, 'S2025'),
(320, '2026-02-24', '08:00:00', '09:30:00', 'Poussin-1-A', 'Mhiri Afif', 0, NULL, 'entrainement', 90, 'S2025'),
(321, '2026-03-03', '08:00:00', '09:30:00', 'Poussin-1-A', 'Mhiri Afif', 0, NULL, 'entrainement', 90, 'S2025'),
(322, '2026-03-10', '08:00:00', '09:30:00', 'Poussin-1-A', 'Mhiri Afif', 0, NULL, 'entrainement', 90, 'S2025'),
(323, '2026-03-17', '08:00:00', '09:30:00', 'Poussin-1-A', 'Mhiri Afif', 0, NULL, 'entrainement', 90, 'S2025'),
(324, '2026-03-24', '08:00:00', '09:30:00', 'Poussin-1-A', 'Mhiri Afif', 0, NULL, 'entrainement', 90, 'S2025'),
(325, '2026-03-31', '08:00:00', '09:30:00', 'Poussin-1-A', 'Mhiri Afif', 0, NULL, 'entrainement', 90, 'S2025'),
(326, '2026-04-07', '08:00:00', '09:30:00', 'Poussin-1-A', 'Mhiri Afif', 0, NULL, 'entrainement', 90, 'S2025'),
(327, '2026-04-14', '08:00:00', '09:30:00', 'Poussin-1-A', 'Mhiri Afif', 0, NULL, 'entrainement', 90, 'S2025'),
(328, '2026-04-21', '08:00:00', '09:30:00', 'Poussin-1-A', 'Mhiri Afif', 0, NULL, 'entrainement', 90, 'S2025'),
(329, '2026-04-28', '08:00:00', '09:30:00', 'Poussin-1-A', 'Mhiri Afif', 0, NULL, 'entrainement', 90, 'S2025'),
(330, '2026-05-05', '08:00:00', '09:30:00', 'Poussin-1-A', 'Mhiri Afif', 0, NULL, 'entrainement', 90, 'S2025'),
(331, '2026-05-12', '08:00:00', '09:30:00', 'Poussin-1-A', 'Mhiri Afif', 0, NULL, 'entrainement', 90, 'S2025'),
(332, '2026-05-19', '08:00:00', '09:30:00', 'Poussin-1-A', 'Mhiri Afif', 0, NULL, 'entrainement', 90, 'S2025'),
(333, '2026-05-26', '08:00:00', '09:30:00', 'Poussin-1-A', 'Mhiri Afif', 0, NULL, 'entrainement', 90, 'S2025'),
(334, '2026-06-02', '08:00:00', '09:30:00', 'Poussin-1-A', 'Mhiri Afif', 0, NULL, 'entrainement', 90, 'S2025'),
(335, '2026-06-09', '08:00:00', '09:30:00', 'Poussin-1-A', 'Mhiri Afif', 0, NULL, 'entrainement', 90, 'S2025'),
(336, '2026-06-16', '08:00:00', '09:30:00', 'Poussin-1-A', 'Mhiri Afif', 0, NULL, 'entrainement', 90, 'S2025'),
(337, '2026-06-23', '08:00:00', '09:30:00', 'Poussin-1-A', 'Mhiri Afif', 0, NULL, 'entrainement', 90, 'S2025'),
(338, '2026-06-30', '08:00:00', '09:30:00', 'Poussin-1-A', 'Mhiri Afif', 0, NULL, 'entrainement', 90, 'S2025'),
(339, '2026-07-07', '08:00:00', '09:30:00', 'Poussin-1-A', 'Mhiri Afif', 0, NULL, 'entrainement', 90, 'S2025'),
(340, '2026-07-14', '08:00:00', '09:30:00', 'Poussin-1-A', 'Mhiri Afif', 0, NULL, 'entrainement', 90, 'S2025'),
(341, '2026-07-21', '08:00:00', '09:30:00', 'Poussin-1-A', 'Mhiri Afif', 0, NULL, 'entrainement', 90, 'S2025'),
(342, '2026-07-28', '08:00:00', '09:30:00', 'Poussin-1-A', 'Mhiri Afif', 0, NULL, 'entrainement', 90, 'S2025'),
(343, '2026-08-04', '08:00:00', '09:30:00', 'Poussin-1-A', 'Mhiri Afif', 0, NULL, 'entrainement', 90, 'S2025'),
(344, '2026-08-11', '08:00:00', '09:30:00', 'Poussin-1-A', 'Mhiri Afif', 0, NULL, 'entrainement', 90, 'S2025'),
(345, '2026-08-18', '08:00:00', '09:30:00', 'Poussin-1-A', 'Mhiri Afif', 0, NULL, 'entrainement', 90, 'S2025'),
(346, '2026-08-25', '08:00:00', '09:30:00', 'Poussin-1-A', 'Mhiri Afif', 0, NULL, 'entrainement', 90, 'S2025'),
(396, '2025-09-23', '10:00:00', '11:00:00', 'Poussin-1-B', 'Zallila Adam', 0, NULL, 'prep_physique', 60, 'S2025'),
(397, '2025-09-30', '10:00:00', '11:00:00', 'Poussin-1-B', 'Zallila Adam', 0, NULL, 'prep_physique', 60, 'S2025'),
(398, '2025-10-07', '10:00:00', '11:00:00', 'Poussin-1-B', 'Zallila Adam', 0, NULL, 'prep_physique', 60, 'S2025'),
(399, '2025-10-14', '10:00:00', '11:00:00', 'Poussin-1-B', 'Zallila Adam', 0, NULL, 'prep_physique', 60, 'S2025'),
(400, '2025-10-21', '10:00:00', '11:00:00', 'Poussin-1-B', 'Zallila Adam', 0, NULL, 'prep_physique', 60, 'S2025'),
(401, '2025-10-28', '10:00:00', '11:00:00', 'Poussin-1-B', 'Ali Mohamed', NULL, NULL, 'prep_physique', 60, 'S2025'),
(402, '2025-11-04', '10:00:00', '11:00:00', 'Poussin-1-B', 'Zallila Adam', 0, NULL, 'prep_physique', 60, 'S2025'),
(403, '2025-11-11', '10:00:00', '11:00:00', 'Poussin-1-B', 'Zallila Adam', 0, NULL, 'prep_physique', 60, 'S2025'),
(404, '2025-11-18', '10:00:00', '11:00:00', 'Poussin-1-B', 'Zallila Adam', 0, NULL, 'prep_physique', 60, 'S2025'),
(405, '2025-11-25', '10:00:00', '11:00:00', 'Poussin-1-B', 'Zallila Adam', 0, NULL, 'prep_physique', 60, 'S2025'),
(406, '2025-12-02', '10:00:00', '11:00:00', 'Poussin-1-B', 'Zallila Adam', 0, NULL, 'prep_physique', 60, 'S2025'),
(407, '2025-12-09', '10:00:00', '11:00:00', 'Poussin-1-B', 'Zallila Adam', 0, NULL, 'prep_physique', 60, 'S2025'),
(408, '2025-12-16', '10:00:00', '11:00:00', 'Poussin-1-B', 'Zallila Adam', 0, NULL, 'prep_physique', 60, 'S2025'),
(409, '2025-12-23', '10:00:00', '11:00:00', 'Poussin-1-B', 'Zallila Adam', 0, NULL, 'prep_physique', 60, 'S2025'),
(410, '2025-12-30', '10:00:00', '11:00:00', 'Poussin-1-B', 'Zallila Adam', 0, NULL, 'prep_physique', 60, 'S2025'),
(411, '2026-01-06', '10:00:00', '11:00:00', 'Poussin-1-B', 'Zallila Adam', 0, NULL, 'prep_physique', 60, 'S2025'),
(412, '2026-01-13', '10:00:00', '11:00:00', 'Poussin-1-B', 'Zallila Adam', 0, NULL, 'prep_physique', 60, 'S2025'),
(413, '2026-01-20', '10:00:00', '11:00:00', 'Poussin-1-B', 'Zallila Adam', 0, NULL, 'prep_physique', 60, 'S2025'),
(414, '2026-01-27', '10:00:00', '11:00:00', 'Poussin-1-B', 'Zallila Adam', 0, NULL, 'prep_physique', 60, 'S2025'),
(415, '2026-02-03', '10:00:00', '11:00:00', 'Poussin-1-B', 'Zallila Adam', 0, NULL, 'prep_physique', 60, 'S2025'),
(416, '2026-02-10', '10:00:00', '11:00:00', 'Poussin-1-B', 'Zallila Adam', 0, NULL, 'prep_physique', 60, 'S2025'),
(417, '2026-02-17', '10:00:00', '11:00:00', 'Poussin-1-B', 'Zallila Adam', 0, NULL, 'prep_physique', 60, 'S2025'),
(418, '2026-02-24', '10:00:00', '11:00:00', 'Poussin-1-B', 'Zallila Adam', 0, NULL, 'prep_physique', 60, 'S2025'),
(419, '2026-03-03', '10:00:00', '11:00:00', 'Poussin-1-B', 'Zallila Adam', 0, NULL, 'prep_physique', 60, 'S2025'),
(420, '2026-03-10', '10:00:00', '11:00:00', 'Poussin-1-B', 'Zallila Adam', 0, NULL, 'prep_physique', 60, 'S2025'),
(421, '2026-03-17', '10:00:00', '11:00:00', 'Poussin-1-B', 'Zallila Adam', 0, NULL, 'prep_physique', 60, 'S2025'),
(422, '2026-03-24', '10:00:00', '11:00:00', 'Poussin-1-B', 'Zallila Adam', 0, NULL, 'prep_physique', 60, 'S2025'),
(423, '2026-03-31', '10:00:00', '11:00:00', 'Poussin-1-B', 'Zallila Adam', 0, NULL, 'prep_physique', 60, 'S2025'),
(424, '2026-04-07', '10:00:00', '11:00:00', 'Poussin-1-B', 'Zallila Adam', 0, NULL, 'prep_physique', 60, 'S2025'),
(425, '2026-04-14', '10:00:00', '11:00:00', 'Poussin-1-B', 'Zallila Adam', 0, NULL, 'prep_physique', 60, 'S2025'),
(426, '2026-04-21', '10:00:00', '11:00:00', 'Poussin-1-B', 'Zallila Adam', 0, NULL, 'prep_physique', 60, 'S2025'),
(427, '2026-04-28', '10:00:00', '11:00:00', 'Poussin-1-B', 'Zallila Adam', 0, NULL, 'prep_physique', 60, 'S2025'),
(428, '2026-05-05', '10:00:00', '11:00:00', 'Poussin-1-B', 'Zallila Adam', 0, NULL, 'prep_physique', 60, 'S2025'),
(429, '2026-05-12', '10:00:00', '11:00:00', 'Poussin-1-B', 'Zallila Adam', 0, NULL, 'prep_physique', 60, 'S2025'),
(430, '2026-05-19', '10:00:00', '11:00:00', 'Poussin-1-B', 'Zallila Adam', 0, NULL, 'prep_physique', 60, 'S2025'),
(431, '2026-05-26', '10:00:00', '11:00:00', 'Poussin-1-B', 'Zallila Adam', 0, NULL, 'prep_physique', 60, 'S2025'),
(432, '2026-06-02', '10:00:00', '11:00:00', 'Poussin-1-B', 'Zallila Adam', 0, NULL, 'prep_physique', 60, 'S2025'),
(433, '2026-06-09', '10:00:00', '11:00:00', 'Poussin-1-B', 'Zallila Adam', 0, NULL, 'prep_physique', 60, 'S2025'),
(434, '2026-06-16', '10:00:00', '11:00:00', 'Poussin-1-B', 'Zallila Adam', 0, NULL, 'prep_physique', 60, 'S2025'),
(435, '2026-06-23', '10:00:00', '11:00:00', 'Poussin-1-B', 'Zallila Adam', 0, NULL, 'prep_physique', 60, 'S2025'),
(436, '2026-06-30', '10:00:00', '11:00:00', 'Poussin-1-B', 'Zallila Adam', 0, NULL, 'prep_physique', 60, 'S2025'),
(437, '2026-07-07', '10:00:00', '11:00:00', 'Poussin-1-B', 'Zallila Adam', 0, NULL, 'prep_physique', 60, 'S2025'),
(438, '2026-07-14', '10:00:00', '11:00:00', 'Poussin-1-B', 'Zallila Adam', 0, NULL, 'prep_physique', 60, 'S2025'),
(439, '2026-07-21', '10:00:00', '11:00:00', 'Poussin-1-B', 'Zallila Adam', 0, NULL, 'prep_physique', 60, 'S2025'),
(440, '2026-07-28', '10:00:00', '11:00:00', 'Poussin-1-B', 'Zallila Adam', 0, NULL, 'prep_physique', 60, 'S2025'),
(441, '2026-08-04', '10:00:00', '11:00:00', 'Poussin-1-B', 'Zallila Adam', 0, NULL, 'prep_physique', 60, 'S2025'),
(442, '2026-08-11', '10:00:00', '11:00:00', 'Poussin-1-B', 'Zallila Adam', 0, NULL, 'prep_physique', 60, 'S2025'),
(443, '2026-08-18', '10:00:00', '11:00:00', 'Poussin-1-B', 'Zallila Adam', 0, NULL, 'prep_physique', 60, 'S2025'),
(444, '2026-08-25', '10:00:00', '11:00:00', 'Poussin-1-B', 'Zallila Adam', 0, NULL, 'prep_physique', 60, 'S2025'),
(494, '2025-09-24', '13:00:00', '14:00:00', 'Ecole_ete-2-A', 'Ali Mohamed', 0, NULL, 'prep_physique', 60, 'S2025'),
(495, '2025-10-01', '13:00:00', '14:00:00', 'Ecole_ete-2-A', 'Ali Mohamed', 0, NULL, 'prep_physique', 60, 'S2025'),
(496, '2025-10-08', '13:00:00', '14:00:00', 'Ecole_ete-2-A', 'Ali Mohamed', 0, NULL, 'prep_physique', 60, 'S2025'),
(497, '2025-10-15', '13:00:00', '14:00:00', 'Ecole_ete-2-A', 'Ali Mohamed', 0, NULL, 'prep_physique', 60, 'S2025'),
(498, '2025-10-22', '13:00:00', '14:00:00', 'Ecole_ete-2-A', 'Ali Mohamed', 0, NULL, 'prep_physique', 60, 'S2025'),
(499, '2025-10-29', '13:00:00', '14:00:00', 'Ecole_ete-2-A', 'Ali Mohamed', 0, NULL, 'prep_physique', 60, 'S2025'),
(500, '2025-11-05', '13:00:00', '14:00:00', 'Ecole_ete-2-A', 'Ali Mohamed', 0, NULL, 'prep_physique', 60, 'S2025'),
(501, '2025-11-12', '13:00:00', '14:00:00', 'Ecole_ete-2-A', 'Ali Mohamed', 0, NULL, 'prep_physique', 60, 'S2025'),
(502, '2025-11-19', '13:00:00', '14:00:00', 'Ecole_ete-2-A', 'Ali Mohamed', 0, NULL, 'prep_physique', 60, 'S2025'),
(503, '2025-11-26', '13:00:00', '14:00:00', 'Ecole_ete-2-A', 'Ali Mohamed', 0, NULL, 'prep_physique', 60, 'S2025'),
(504, '2025-12-03', '13:00:00', '14:00:00', 'Ecole_ete-2-A', 'Ali Mohamed', 0, NULL, 'prep_physique', 60, 'S2025'),
(505, '2025-12-10', '13:00:00', '14:00:00', 'Ecole_ete-2-A', 'Ali Mohamed', 0, NULL, 'prep_physique', 60, 'S2025'),
(506, '2025-12-17', '13:00:00', '14:00:00', 'Ecole_ete-2-A', 'Ali Mohamed', 0, NULL, 'prep_physique', 60, 'S2025'),
(507, '2025-12-24', '13:00:00', '14:00:00', 'Ecole_ete-2-A', 'Ali Mohamed', 0, NULL, 'prep_physique', 60, 'S2025'),
(508, '2025-12-31', '13:00:00', '14:00:00', 'Ecole_ete-2-A', 'Ali Mohamed', 0, NULL, 'prep_physique', 60, 'S2025'),
(509, '2026-01-07', '13:00:00', '14:00:00', 'Ecole_ete-2-A', 'Ali Mohamed', 0, NULL, 'prep_physique', 60, 'S2025'),
(510, '2026-01-14', '13:00:00', '14:00:00', 'Ecole_ete-2-A', 'Ali Mohamed', 0, NULL, 'prep_physique', 60, 'S2025'),
(511, '2026-01-21', '13:00:00', '14:00:00', 'Ecole_ete-2-A', 'Ali Mohamed', 0, NULL, 'prep_physique', 60, 'S2025'),
(512, '2026-01-28', '13:00:00', '14:00:00', 'Ecole_ete-2-A', 'Ali Mohamed', 0, NULL, 'prep_physique', 60, 'S2025'),
(513, '2026-02-04', '13:00:00', '14:00:00', 'Ecole_ete-2-A', 'Ali Mohamed', 0, NULL, 'prep_physique', 60, 'S2025'),
(514, '2026-02-11', '13:00:00', '14:00:00', 'Ecole_ete-2-A', 'Ali Mohamed', 0, NULL, 'prep_physique', 60, 'S2025'),
(515, '2026-02-18', '13:00:00', '14:00:00', 'Ecole_ete-2-A', 'Ali Mohamed', 0, NULL, 'prep_physique', 60, 'S2025'),
(516, '2026-02-25', '13:00:00', '14:00:00', 'Ecole_ete-2-A', 'Ali Mohamed', 0, NULL, 'prep_physique', 60, 'S2025'),
(517, '2026-03-04', '13:00:00', '14:00:00', 'Ecole_ete-2-A', 'Ali Mohamed', 0, NULL, 'prep_physique', 60, 'S2025'),
(518, '2026-03-11', '13:00:00', '14:00:00', 'Ecole_ete-2-A', 'Ali Mohamed', 0, NULL, 'prep_physique', 60, 'S2025'),
(519, '2026-03-18', '13:00:00', '14:00:00', 'Ecole_ete-2-A', 'Ali Mohamed', 0, NULL, 'prep_physique', 60, 'S2025'),
(520, '2026-03-25', '13:00:00', '14:00:00', 'Ecole_ete-2-A', 'Ali Mohamed', 0, NULL, 'prep_physique', 60, 'S2025'),
(521, '2026-04-01', '13:00:00', '14:00:00', 'Ecole_ete-2-A', 'Ali Mohamed', 0, NULL, 'prep_physique', 60, 'S2025'),
(522, '2026-04-08', '13:00:00', '14:00:00', 'Ecole_ete-2-A', 'Ali Mohamed', 0, NULL, 'prep_physique', 60, 'S2025'),
(523, '2026-04-15', '13:00:00', '14:00:00', 'Ecole_ete-2-A', 'Ali Mohamed', 0, NULL, 'prep_physique', 60, 'S2025'),
(524, '2026-04-22', '13:00:00', '14:00:00', 'Ecole_ete-2-A', 'Ali Mohamed', 0, NULL, 'prep_physique', 60, 'S2025'),
(525, '2026-04-29', '13:00:00', '14:00:00', 'Ecole_ete-2-A', 'Ali Mohamed', 0, NULL, 'prep_physique', 60, 'S2025'),
(526, '2026-05-06', '13:00:00', '14:00:00', 'Ecole_ete-2-A', 'Ali Mohamed', 0, NULL, 'prep_physique', 60, 'S2025'),
(527, '2026-05-13', '13:00:00', '14:00:00', 'Ecole_ete-2-A', 'Ali Mohamed', 0, NULL, 'prep_physique', 60, 'S2025'),
(528, '2026-05-20', '13:00:00', '14:00:00', 'Ecole_ete-2-A', 'Ali Mohamed', 0, NULL, 'prep_physique', 60, 'S2025'),
(529, '2026-05-27', '13:00:00', '14:00:00', 'Ecole_ete-2-A', 'Ali Mohamed', 0, NULL, 'prep_physique', 60, 'S2025'),
(530, '2026-06-03', '13:00:00', '14:00:00', 'Ecole_ete-2-A', 'Ali Mohamed', 0, NULL, 'prep_physique', 60, 'S2025'),
(531, '2026-06-10', '13:00:00', '14:00:00', 'Ecole_ete-2-A', 'Ali Mohamed', 0, NULL, 'prep_physique', 60, 'S2025'),
(532, '2026-06-17', '13:00:00', '14:00:00', 'Ecole_ete-2-A', 'Ali Mohamed', 0, NULL, 'prep_physique', 60, 'S2025'),
(533, '2026-06-24', '13:00:00', '14:00:00', 'Ecole_ete-2-A', 'Ali Mohamed', 0, NULL, 'prep_physique', 60, 'S2025'),
(534, '2026-07-01', '13:00:00', '14:00:00', 'Ecole_ete-2-A', 'Ali Mohamed', 0, NULL, 'prep_physique', 60, 'S2025'),
(535, '2026-07-08', '13:00:00', '14:00:00', 'Ecole_ete-2-A', 'Ali Mohamed', 0, NULL, 'prep_physique', 60, 'S2025'),
(536, '2026-07-15', '13:00:00', '14:00:00', 'Ecole_ete-2-A', 'Ali Mohamed', 0, NULL, 'prep_physique', 60, 'S2025'),
(537, '2026-07-22', '13:00:00', '14:00:00', 'Ecole_ete-2-A', 'Ali Mohamed', 0, NULL, 'prep_physique', 60, 'S2025'),
(538, '2026-07-29', '13:00:00', '14:00:00', 'Ecole_ete-2-A', 'Ali Mohamed', 0, NULL, 'prep_physique', 60, 'S2025'),
(539, '2026-08-05', '13:00:00', '14:00:00', 'Ecole_ete-2-A', 'Ali Mohamed', 0, NULL, 'prep_physique', 60, 'S2025'),
(540, '2026-08-12', '13:00:00', '14:00:00', 'Ecole_ete-2-A', 'Ali Mohamed', 0, NULL, 'prep_physique', 60, 'S2025'),
(541, '2026-08-19', '13:00:00', '14:00:00', 'Ecole_ete-2-A', 'Ali Mohamed', 0, NULL, 'prep_physique', 60, 'S2025'),
(542, '2026-08-26', '13:00:00', '14:00:00', 'Ecole_ete-2-A', 'Ali Mohamed', 0, NULL, 'prep_physique', 60, 'S2025'),
(543, '2025-09-24', '08:00:00', '09:30:00', 'Ecole_ete-2-A', 'Ali Mohamed', 1, NULL, 'entrainement', 90, 'S2025'),
(544, '2025-09-26', '08:00:00', '09:30:00', 'KD-1-B', 'Hdaya Aya', 1, NULL, 'entrainement', 90, 'S2025'),
(545, '2025-09-26', '09:30:00', '11:00:00', 'Benjamin-1-C', 'Jebri Amine', 1, NULL, 'entrainement', 90, 'S2025'),
(546, '2025-10-23', '18:00:00', '19:30:00', 'Poussin-1-B', 'Zallila Adam', 3, NULL, 'entrainement', 90, 'S2025'),
(547, '2025-10-23', '18:00:00', '19:30:00', 'Benjamin-1-C', 'Jebri Amine', 8, NULL, 'prep_physique', 90, 'S2025'),
(548, '2025-10-24', '18:00:00', '19:30:00', 'Poussin-1-B', 'Zallila Adam', 5, NULL, 'entrainement', 90, 'S2025'),
(549, '2025-10-31', '18:00:00', '19:30:00', 'Poussin-1-B', 'Zallila Adam', 5, NULL, 'entrainement', 90, 'S2025'),
(550, '2025-11-07', '18:00:00', '19:30:00', 'Poussin-1-B', 'Zallila Adam', 5, NULL, 'entrainement', 90, 'S2025'),
(551, '2025-11-14', '18:00:00', '19:30:00', 'Poussin-1-B', 'Zallila Adam', 5, NULL, 'entrainement', 90, 'S2025'),
(552, '2025-11-21', '18:00:00', '19:30:00', 'Poussin-1-B', 'Zallila Adam', 5, NULL, 'entrainement', 90, 'S2025'),
(553, '2025-11-28', '18:00:00', '19:30:00', 'Poussin-1-B', 'Zallila Adam', 5, NULL, 'entrainement', 90, 'S2025'),
(554, '2025-12-05', '18:00:00', '19:30:00', 'Poussin-1-B', 'Zallila Adam', 5, NULL, 'entrainement', 90, 'S2025'),
(555, '2025-12-12', '18:00:00', '19:30:00', 'Poussin-1-B', 'Zallila Adam', 5, NULL, 'entrainement', 90, 'S2025'),
(556, '2025-12-19', '18:00:00', '19:30:00', 'Poussin-1-B', 'Zallila Adam', 5, NULL, 'entrainement', 90, 'S2025'),
(557, '2025-12-26', '18:00:00', '19:30:00', 'Poussin-1-B', 'Zallila Adam', 5, NULL, 'entrainement', 90, 'S2025'),
(558, '2026-01-02', '18:00:00', '19:30:00', 'Poussin-1-B', 'Zallila Adam', 5, NULL, 'entrainement', 90, 'S2025'),
(559, '2026-01-09', '18:00:00', '19:30:00', 'Poussin-1-B', 'Zallila Adam', 5, NULL, 'entrainement', 90, 'S2025'),
(560, '2026-01-16', '18:00:00', '19:30:00', 'Poussin-1-B', 'Zallila Adam', 5, NULL, 'entrainement', 90, 'S2025'),
(561, '2026-01-23', '18:00:00', '19:30:00', 'Poussin-1-B', 'Zallila Adam', 5, NULL, 'entrainement', 90, 'S2025'),
(562, '2026-01-30', '18:00:00', '19:30:00', 'Poussin-1-B', 'Zallila Adam', 5, NULL, 'entrainement', 90, 'S2025'),
(563, '2026-02-06', '18:00:00', '19:30:00', 'Poussin-1-B', 'Zallila Adam', 5, NULL, 'entrainement', 90, 'S2025'),
(564, '2026-02-13', '18:00:00', '19:30:00', 'Poussin-1-B', 'Zallila Adam', 5, NULL, 'entrainement', 90, 'S2025'),
(565, '2026-02-20', '18:00:00', '19:30:00', 'Poussin-1-B', 'Zallila Adam', 5, NULL, 'entrainement', 90, 'S2025'),
(566, '2026-02-27', '18:00:00', '19:30:00', 'Poussin-1-B', 'Zallila Adam', 5, NULL, 'entrainement', 90, 'S2025'),
(567, '2026-03-06', '18:00:00', '19:30:00', 'Poussin-1-B', 'Zallila Adam', 5, NULL, 'entrainement', 90, 'S2025'),
(568, '2026-03-13', '18:00:00', '19:30:00', 'Poussin-1-B', 'Zallila Adam', 5, NULL, 'entrainement', 90, 'S2025'),
(569, '2026-03-20', '18:00:00', '19:30:00', 'Poussin-1-B', 'Zallila Adam', 5, NULL, 'entrainement', 90, 'S2025'),
(570, '2026-03-27', '18:00:00', '19:30:00', 'Poussin-1-B', 'Zallila Adam', 5, NULL, 'entrainement', 90, 'S2025'),
(571, '2026-04-03', '18:00:00', '19:30:00', 'Poussin-1-B', 'Zallila Adam', 5, NULL, 'entrainement', 90, 'S2025'),
(572, '2026-04-10', '18:00:00', '19:30:00', 'Poussin-1-B', 'Zallila Adam', 5, NULL, 'entrainement', 90, 'S2025'),
(573, '2026-04-17', '18:00:00', '19:30:00', 'Poussin-1-B', 'Zallila Adam', 5, NULL, 'entrainement', 90, 'S2025'),
(574, '2026-04-24', '18:00:00', '19:30:00', 'Poussin-1-B', 'Zallila Adam', 5, NULL, 'entrainement', 90, 'S2025'),
(575, '2026-05-01', '18:00:00', '19:30:00', 'Poussin-1-B', 'Zallila Adam', 5, NULL, 'entrainement', 90, 'S2025'),
(576, '2026-05-08', '18:00:00', '19:30:00', 'Poussin-1-B', 'Zallila Adam', 5, NULL, 'entrainement', 90, 'S2025'),
(577, '2026-05-15', '18:00:00', '19:30:00', 'Poussin-1-B', 'Zallila Adam', 5, NULL, 'entrainement', 90, 'S2025'),
(578, '2026-05-22', '18:00:00', '19:30:00', 'Poussin-1-B', 'Zallila Adam', 5, NULL, 'entrainement', 90, 'S2025'),
(579, '2026-05-29', '18:00:00', '19:30:00', 'Poussin-1-B', 'Zallila Adam', 5, NULL, 'entrainement', 90, 'S2025'),
(580, '2026-06-05', '18:00:00', '19:30:00', 'Poussin-1-B', 'Zallila Adam', 5, NULL, 'entrainement', 90, 'S2025'),
(581, '2026-06-12', '18:00:00', '19:30:00', 'Poussin-1-B', 'Zallila Adam', 5, NULL, 'entrainement', 90, 'S2025'),
(582, '2026-06-19', '18:00:00', '19:30:00', 'Poussin-1-B', 'Zallila Adam', 5, NULL, 'entrainement', 90, 'S2025'),
(583, '2026-06-26', '18:00:00', '19:30:00', 'Poussin-1-B', 'Zallila Adam', 5, NULL, 'entrainement', 90, 'S2025'),
(584, '2026-07-03', '18:00:00', '19:30:00', 'Poussin-1-B', 'Zallila Adam', 5, NULL, 'entrainement', 90, 'S2025'),
(585, '2026-07-10', '18:00:00', '19:30:00', 'Poussin-1-B', 'Zallila Adam', 5, NULL, 'entrainement', 90, 'S2025'),
(586, '2026-07-17', '18:00:00', '19:30:00', 'Poussin-1-B', 'Zallila Adam', 5, NULL, 'entrainement', 90, 'S2025'),
(587, '2026-07-24', '18:00:00', '19:30:00', 'Poussin-1-B', 'Zallila Adam', 5, NULL, 'entrainement', 90, 'S2025'),
(588, '2026-07-31', '18:00:00', '19:30:00', 'Poussin-1-B', 'Zallila Adam', 5, NULL, 'entrainement', 90, 'S2025'),
(589, '2026-08-07', '18:00:00', '19:30:00', 'Poussin-1-B', 'Zallila Adam', 5, NULL, 'entrainement', 90, 'S2025'),
(590, '2026-08-14', '18:00:00', '19:30:00', 'Poussin-1-B', 'Zallila Adam', 5, NULL, 'entrainement', 90, 'S2025'),
(591, '2026-08-21', '18:00:00', '19:30:00', 'Poussin-1-B', 'Zallila Adam', 5, NULL, 'entrainement', 90, 'S2025'),
(592, '2026-08-28', '18:00:00', '19:30:00', 'Poussin-1-B', 'Zallila Adam', 5, NULL, 'entrainement', 90, 'S2025'),
(595, '2025-10-27', '12:30:00', '14:30:00', 'Poussin-1-A', 'Zallila Adam', 5, NULL, 'entrainement', 120, 'S2025');

-- --------------------------------------------------------

--
-- Structure de la table `tournois`
--

CREATE TABLE `tournois` (
  `id` int(11) NOT NULL,
  `nom_tournoi` varchar(100) NOT NULL,
  `nombre_groupes` int(11) NOT NULL,
  `joueurs_par_groupe` int(11) NOT NULL,
  `qualifies_par_groupe` int(11) NOT NULL,
  `dates_matches` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL CHECK (json_valid(`dates_matches`)),
  `matches` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL CHECK (json_valid(`matches`)),
  `date_creation` datetime DEFAULT current_timestamp(),
  `date_debut` datetime NOT NULL,
  `date_fin` datetime NOT NULL,
  `statut` varchar(20) NOT NULL DEFAULT 'en_attente'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `tournois`
--

INSERT INTO `tournois` (`id`, `nom_tournoi`, `nombre_groupes`, `joueurs_par_groupe`, `qualifies_par_groupe`, `dates_matches`, `matches`, `date_creation`, `date_debut`, `date_fin`, `statut`) VALUES
(8, 'egerge', 4, 8, 2, '{}', '{\"phase_groupes\": {\"groupe_1\": {\"nom\": \"Groupe 1\", \"participants\": [\"Joueur 1\", \"Joueur 2\", \"Joueur 3\", \"Joueur 4\", \"Joueur 5\", \"Joueur 6\", \"Joueur 7\", \"Joueur 8\"], \"qualifies\": [\"Joueur 1\", \"Joueur 2\"]}, \"groupe_2\": {\"nom\": \"Groupe 2\", \"participants\": [\"Joueur 1\", \"Joueur 2\", \"Joueur 3\", \"Joueur 4\", \"Joueur 5\", \"Joueur 6\", \"Joueur 7\", \"Joueur 8\"], \"qualifies\": [\"Joueur 1\", \"Joueur 2\"]}, \"groupe_3\": {\"nom\": \"Groupe 3\", \"participants\": [\"Joueur 1\", \"Joueur 2\", \"Joueur 3\", \"Joueur 4\", \"Joueur 5\", \"Joueur 6\", \"Joueur 7\", \"Joueur 8\"], \"qualifies\": [\"Joueur 1\", \"Joueur 2\"]}, \"groupe_4\": {\"nom\": \"Groupe 4\", \"participants\": [\"Joueur 1\", \"Joueur 2\", \"Joueur 3\", \"Joueur 4\", \"Joueur 5\", \"Joueur 6\", \"Joueur 7\", \"Joueur 8\"], \"qualifies\": [\"Joueur 1\", \"Joueur 2\"]}}, \"phase_finale\": {\"quart\": [{\"match\": \"Quart 1\", \"joueurs\": []}, {\"match\": \"Quart 2\", \"joueurs\": []}, {\"match\": \"Quart 3\", \"joueurs\": []}, {\"match\": \"Quart 4\", \"joueurs\": []}], \"demi\": [], \"finale\": null}}', '2025-05-08 08:16:09', '2025-05-08 08:16:00', '2025-05-09 08:16:00', 'en_attente');

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
(3, 'manager', '03ac674216f3e15c761ee1a5e255f067953623c8b388b4459e13f978d7c846f4', 'directeur_technique'),
(7, 'Zallila.Adam', '03ac674216f3e15c761ee1a5e255f067953623c8b388b4459e13f978d7c846f4', 'entraineur'),
(8, 'jaber.ons', 'a18ceb2154111dd7e9bdfe59a36ae187ef6880bdbe676fb47ca1bb796f3dcbc1', 'entraineur'),
(9, 'mhiri.afif', '03ac674216f3e15c761ee1a5e255f067953623c8b388b4459e13f978d7c846f4', 'entraineur'),
(10, 'jebri.amine', 'a18ceb2154111dd7e9bdfe59a36ae187ef6880bdbe676fb47ca1bb796f3dcbc1', 'entraineur'),
(11, 'jegham.anis', 'a18ceb2154111dd7e9bdfe59a36ae187ef6880bdbe676fb47ca1bb796f3dcbc1', 'entraineur'),
(12, 'hdaya.aya', 'a18ceb2154111dd7e9bdfe59a36ae187ef6880bdbe676fb47ca1bb796f3dcbc1', 'entraineur'),
(13, 'gaaloul.ilhem', 'a18ceb2154111dd7e9bdfe59a36ae187ef6880bdbe676fb47ca1bb796f3dcbc1', 'entraineur'),
(14, 'kbaili.nour', 'a18ceb2154111dd7e9bdfe59a36ae187ef6880bdbe676fb47ca1bb796f3dcbc1', 'entraineur'),
(15, 'kharrat.ramzi', 'a18ceb2154111dd7e9bdfe59a36ae187ef6880bdbe676fb47ca1bb796f3dcbc1', 'entraineur'),
(16, 'missoum.walid', 'a18ceb2154111dd7e9bdfe59a36ae187ef6880bdbe676fb47ca1bb796f3dcbc1', 'entraineur'),
(17, 'user', '04f8996da763b7a969b1028ee3007569eaf3a635486ddab211d512c85b9df8fb', 'admin'),
(18, 'aaa.bbb', 'a18ceb2154111dd7e9bdfe59a36ae187ef6880bdbe676fb47ca1bb796f3dcbc1', 'entraineur'),
(20, 'ali.mohamed', 'a18ceb2154111dd7e9bdfe59a36ae187ef6880bdbe676fb47ca1bb796f3dcbc1', 'entraineur'),
(21, 'benali.ali', 'a18ceb2154111dd7e9bdfe59a36ae187ef6880bdbe676fb47ca1bb796f3dcbc1', 'entraineur'),
(22, 'test.test', 'a18ceb2154111dd7e9bdfe59a36ae187ef6880bdbe676fb47ca1bb796f3dcbc1', 'entraineur');

--
-- Index pour les tables déchargées
--

--
-- Index pour la table `adherent`
--
ALTER TABLE `adherent`
  ADD PRIMARY KEY (`adherent_id`);

--
-- Index pour la table `autres_paiements`
--
ALTER TABLE `autres_paiements`
  ADD PRIMARY KEY (`id`);

--
-- Index pour la table `bon_de_recette`
--
ALTER TABLE `bon_de_recette`
  ADD PRIMARY KEY (`id_bon`);

--
-- Index pour la table `cotisations`
--
ALTER TABLE `cotisations`
  ADD PRIMARY KEY (`id_cotisation`);

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
-- Index pour la table `locations_terrains`
--
ALTER TABLE `locations_terrains`
  ADD PRIMARY KEY (`id_location`);

--
-- Index pour la table `match`
--
ALTER TABLE `match`
  ADD PRIMARY KEY (`id_match`),
  ADD KEY `match_suivant` (`match_suivant`),
  ADD KEY `idx_match_tournoi` (`id_tournoi`);

--
-- Index pour la table `messages`
--
ALTER TABLE `messages`
  ADD PRIMARY KEY (`id`);

--
-- Index pour la table `paiements`
--
ALTER TABLE `paiements`
  ADD PRIMARY KEY (`id_paiement`);

--
-- Index pour la table `participanttournoi`
--
ALTER TABLE `participanttournoi`
  ADD PRIMARY KEY (`id_participation`),
  ADD KEY `idx_participant_tournoi` (`id_tournoi`,`poule`);

--
-- Index pour la table `presence`
--
ALTER TABLE `presence`
  ADD PRIMARY KEY (`id_presence`);

--
-- Index pour la table `presence_entraineurs`
--
ALTER TABLE `presence_entraineurs`
  ADD PRIMARY KEY (`id_presence`),
  ADD KEY `seance_id` (`seance_id`);

--
-- Index pour la table `reservations`
--
ALTER TABLE `reservations`
  ADD PRIMARY KEY (`id_reservation`);

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
-- Index pour la table `tournois`
--
ALTER TABLE `tournois`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_tournois_statut` (`statut`);

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
  MODIFY `adherent_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=34;

--
-- AUTO_INCREMENT pour la table `autres_paiements`
--
ALTER TABLE `autres_paiements`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT pour la table `bon_de_recette`
--
ALTER TABLE `bon_de_recette`
  MODIFY `id_bon` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT pour la table `cotisations`
--
ALTER TABLE `cotisations`
  MODIFY `id_cotisation` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=27;

--
-- AUTO_INCREMENT pour la table `depense`
--
ALTER TABLE `depense`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=10;

--
-- AUTO_INCREMENT pour la table `entraineur`
--
ALTER TABLE `entraineur`
  MODIFY `id_entraineur` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=25;

--
-- AUTO_INCREMENT pour la table `groupe`
--
ALTER TABLE `groupe`
  MODIFY `id_groupe` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=27;

--
-- AUTO_INCREMENT pour la table `locations_terrains`
--
ALTER TABLE `locations_terrains`
  MODIFY `id_location` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT pour la table `match`
--
ALTER TABLE `match`
  MODIFY `id_match` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT pour la table `messages`
--
ALTER TABLE `messages`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=14;

--
-- AUTO_INCREMENT pour la table `paiements`
--
ALTER TABLE `paiements`
  MODIFY `id_paiement` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=50;

--
-- AUTO_INCREMENT pour la table `participanttournoi`
--
ALTER TABLE `participanttournoi`
  MODIFY `id_participation` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT pour la table `presence`
--
ALTER TABLE `presence`
  MODIFY `id_presence` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=14;

--
-- AUTO_INCREMENT pour la table `presence_entraineurs`
--
ALTER TABLE `presence_entraineurs`
  MODIFY `id_presence` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=9;

--
-- AUTO_INCREMENT pour la table `reservations`
--
ALTER TABLE `reservations`
  MODIFY `id_reservation` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT pour la table `revenu`
--
ALTER TABLE `revenu`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT pour la table `seances`
--
ALTER TABLE `seances`
  MODIFY `seance_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=596;

--
-- AUTO_INCREMENT pour la table `tournois`
--
ALTER TABLE `tournois`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=9;

--
-- AUTO_INCREMENT pour la table `utilisateurs`
--
ALTER TABLE `utilisateurs`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=23;

--
-- Contraintes pour les tables déchargées
--

--
-- Contraintes pour la table `presence_entraineurs`
--
ALTER TABLE `presence_entraineurs`
  ADD CONSTRAINT `presence_entraineurs_ibfk_1` FOREIGN KEY (`seance_id`) REFERENCES `seances` (`seance_id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
