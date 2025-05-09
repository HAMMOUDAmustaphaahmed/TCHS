-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Hôte : 127.0.0.1
-- Généré le : ven. 09 mai 2025 à 16:12
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
(6, 'hammouda', 'ahmed', '1996-08-30', 'M', '2025-01-20', '54391747', '54391747', 'Compétitif', 'Non', 1, 'Ecole-1-A', 'Mhiri Afif', 'ahmed@gmail.com', 'N', 'Non-Actif'),
(7, 'mohamed', 'ali', '1990-01-01', 'M', '2025-01-20', '12345678', '123546789', 'Loisir', 'Non', 2, 'john.doe', 'john doe', 'user@gmail.com', 'N', 'Actif'),
(8, 'mohamed', 'saleh', '1994-01-01', 'M', '2025-01-20', '1234', '12345', 'Loisir', 'Non', 3, 'john.doe', 'john doe', 'user@gmail.com', 'N', 'Actif'),
(9, 'Flen', 'Ben Flen', '2025-01-22', 'M', '2025-01-22', '1234', '1234', 'Loisir', 'Non', 4, 'loisir', 'john doe', 'flen@gmail.com', 'N', 'Actif'),
(10, 'Abdelmaksoud', 'Thameur', '2000-04-06', 'F', '2025-01-22', '28425595', '', 'N/D', 'Non', 5, 'X', 'test tedst', '', 'N', 'Actif'),
(11, 'Foulani', 'Foulen', '2025-01-22', 'M', '2025-01-22', '1234', '', 'Compétitif', 'Non', 6, 'Poussin-1-A', 'Mhiri Afif', '', 'N', 'Actif'),
(12, 'aaa', 'aaa', '2025-01-22', 'M', '2025-01-22', '134', '', 'Ecole d\'été', 'Non', 7, 'Poussin-1-A', 'Mhiri Afif', 'a@gmail.com', 'N', 'Actif'),
(13, 'Da7ee7', 'Da7ee7', '2025-01-22', 'M', '2025-01-22', '1234', '', NULL, 'Non', 8, 'Poussin-1-A', 'Zallila Adam', 'da7ee7@gmail.com', 'N', 'Actif'),
(14, 'mohamed', 'mohamed', '1990-01-01', 'M', '2025-05-06', '12345678', '12345677', 'N/D', 'Non', 9, 'Ecole-1-A', 'Mhiri Afif', 'mohamed.mohamed@gmail.com', 'N', 'Actif');

-- --------------------------------------------------------

--
-- Structure de la table `autres_paiements`
--

CREATE TABLE `autres_paiements` (
  `id` int(11) NOT NULL,
  `amount` decimal(10,2) NOT NULL,
  `category` varchar(50) NOT NULL,
  `date` date NOT NULL,
  `description` text NOT NULL,
  `timestamp` timestamp NOT NULL DEFAULT current_timestamp(),
  `company_name` varchar(100) NOT NULL,
  `bank_name` varchar(100) NOT NULL,
  `rib` varchar(100) DEFAULT NULL,
  `location` varchar(200) DEFAULT NULL,
  `documents` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`documents`))
) ;

-- --------------------------------------------------------

--
-- Structure de la table `autres_paiements_backup`
--

CREATE TABLE `autres_paiements_backup` (
  `id` int(11) NOT NULL DEFAULT 0,
  `type` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `amount` decimal(10,2) NOT NULL,
  `category` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `date` date NOT NULL,
  `description` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `timestamp` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `autres_paiements_backup`
--

INSERT INTO `autres_paiements_backup` (`id`, `type`, `amount`, `category`, `date`, `description`, `timestamp`) VALUES
(1, 'revenue', 123.00, 'other', '2025-05-08', 'qefzefzef', '2025-05-08 10:17:25'),
(2, 'expense', 99999999.99, 'rent', '2025-05-08', 'sdvsdvsdvsdv', '2025-05-08 10:17:45');

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
  `montant_cotisation` float NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `cotisations`
--

INSERT INTO `cotisations` (`id_cotisation`, `nom_cotisation`, `montant_cotisation`) VALUES
(12, 'Poussin-1-A', 100),
(13, 'Poussin-1-B', 200);

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
  `status` enum('Actif','Non-Actif') NOT NULL,
  `tel` varchar(100) DEFAULT NULL,
  `addresse` varchar(100) DEFAULT NULL,
  `compte_bancaire` varchar(100) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `entraineur`
--

INSERT INTO `entraineur` (`id_entraineur`, `nom`, `prenom`, `sexe`, `type_abonnement`, `status`, `tel`, `addresse`, `compte_bancaire`) VALUES
(1, 'test', 'tedst', 'M', 'N/D', 'Non-Actif', NULL, NULL, NULL),
(10, 'john', 'doe', 'M', 'Loisir', 'Actif', NULL, NULL, NULL),
(11, 'Zallila', 'Adam', 'M', 'Compétitif', 'Actif', NULL, NULL, NULL),
(12, 'Jaber', 'Ons', 'F', 'Directeur Technique', 'Actif', '1234', 'rue x', '123456789'),
(13, 'Mhiri', 'Afif', 'M', 'N/D', 'Actif', '1234', 'x', '1234'),
(14, 'Jebri', 'Amine', 'M', 'N/D', 'Actif', '1234', 'x', '1234'),
(15, 'Jegham', 'Anis', 'M', 'N/D', 'Actif', '1234', 'x', '1234'),
(16, 'Hdaya', 'Aya', 'F', 'N/D', 'Actif', '1234', 'x', '1234'),
(17, 'Gaaloul', 'Ilhem', 'F', 'N/D', 'Actif', '1234', 'x', '1234'),
(18, 'Kbaili', 'Nour', 'F', 'N/D', 'Actif', '1234', 'x', '1234'),
(19, 'Kharrat', 'Ramzi', 'M', 'N/D', 'Actif', '1234', 'x', '1234'),
(20, 'Missoum', 'Walid', 'M', 'N/D', 'Actif', '1234', 'x', '1234'),
(21, 'aaa', 'bbb', 'M', 'Adjoint', 'Actif', '12345678', 'aaaaaa', '123456789');

-- --------------------------------------------------------

--
-- Structure de la table `groupe`
--

CREATE TABLE `groupe` (
  `id_groupe` int(11) NOT NULL,
  `nom_groupe` varchar(100) NOT NULL,
  `entraineur_nom` varchar(50) NOT NULL,
  `type_abonnement` varchar(50) NOT NULL,
  `categorie` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `groupe`
--

INSERT INTO `groupe` (`id_groupe`, `nom_groupe`, `entraineur_nom`, `type_abonnement`, `categorie`) VALUES
(7, 'Poussin-1-A', 'Mhiri Afif', 'Compétitif', 'Poussin'),
(8, 'Poussin-1-B', 'Zallila Adam', 'Compétitif', 'Poussin'),
(9, 'Lutin-1-A', 'Kharrat Ramzi', 'Loisir', 'Lutin'),
(10, 'Lutin-1-B', 'Kharrat Ramzi', 'Loisir', 'Lutin'),
(11, 'Benjamin-1-A', 'Missoum Walid', 'N/D', 'Benjamin'),
(12, 'Benjamin-1-B', 'Missoum Walid', 'N/D', 'Benjamin'),
(13, 'Minime-1-A', 'Gaaloul Ilhem', 'N/D', 'Minime'),
(14, 'Minime-1-B', 'Gaaloul Ilhem', 'N/D', 'Minime'),
(15, 'KD-1-A', 'Hdaya Aya', 'N/D', 'KD'),
(16, 'KD-1-B', 'Hdaya Aya', 'N/D', 'KD'),
(18, 'Ecole-1-A', 'Mhiri Afif', 'N/D', 'Ecole');

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
  `code_saison` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `paiements`
--

INSERT INTO `paiements` (`id_paiement`, `matricule_adherent`, `numero_bon`, `numero_carnet`, `date_paiement`, `montant`, `total_montant_paye`, `montant_paye`, `montant_reste`, `type_reglement`, `numero_cheque`, `banque`, `cotisation`, `remise`, `code_saison`) VALUES
(25, '2', 1, 1, '2025-01-28 16:19:40', 450.00, 300, 300.00, 150.00, 'chèque', '123456789', 'BIAT', 500.00, 10.00, ''),
(26, '2', 2, 1, '2025-01-28 16:40:44', 450.00, 100, 100.00, 350.00, 'chèque', '123486', 'x', 500.00, 10.00, ''),
(27, '1', 3, 1, '2025-01-29 16:36:56', 665.00, 500, 500.00, 165.00, 'chèque', '123456789', 'x', 700.00, 5.00, 'S2025'),
(28, '2', 4, 1, '2025-01-29 17:46:49', 450.00, 50, 50.00, 400.00, 'espèce', NULL, NULL, 500.00, 10.00, 'S2025'),
(29, '5', 5, 1, '2025-02-07 08:20:21', 450.00, 200, 200.00, 250.00, 'espèce', NULL, NULL, 500.00, 10.00, 'S2025'),
(30, '4', 6, 1, '2025-02-07 09:34:14', 540.00, 300, 300.00, 240.00, 'espèce', NULL, NULL, 600.00, 10.00, 'S2025'),
(31, '6', 7, 1, '2025-02-07 09:39:08', 250.00, 100, 100.00, 150.00, 'espèce', NULL, NULL, 250.00, 0.00, 'S2025'),
(32, '1', 8, 1, '2025-02-09 13:48:50', 665.00, 165, 165.00, 500.00, 'espèce', NULL, NULL, 700.00, 5.00, 'S2025');

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
  `adherent_matricule` varchar(50) NOT NULL,
  `entraineur_nom` varchar(100) NOT NULL,
  `date_seance` date NOT NULL,
  `heure_debut` time NOT NULL,
  `est_present` enum('O','N') NOT NULL DEFAULT 'N'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `presence`
--

INSERT INTO `presence` (`id_presence`, `groupe_nom`, `adherent_matricule`, `entraineur_nom`, `date_seance`, `heure_debut`, `est_present`) VALUES
(1, 'loisir', '4', 'john doe', '2025-01-22', '10:30:00', 'O'),
(2, 'loisir', '4', 'john doe', '2025-01-22', '10:30:00', 'N'),
(3, 'groupe_onsjaber', '8', 'Jaber Ons', '2025-01-22', '16:30:00', 'O'),
(4, 'groupe_onsjaber', '8', 'Jaber Ons', '2025-01-22', '16:30:00', 'N');

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
  `terrain` int(11) NOT NULL,
  `adherents_matricules` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `seances`
--

INSERT INTO `seances` (`seance_id`, `date`, `heure_debut`, `heure_fin`, `groupe`, `entraineur`, `terrain`, `adherents_matricules`) VALUES
(6, '2025-01-29', '12:30:00', '14:00:00', 'Poussin-1-B', 'Kharrat Ramzi', 2, NULL),
(10, '2025-01-16', '11:00:00', '12:30:00', 'Lutin-1-A', 'Kharrat Ramzi', 3, NULL),
(15, '2025-01-23', '08:00:00', '09:30:00', 'Lutin-1-A', 'Kharrat Ramzi', 1, NULL),
(17, '2025-01-20', '08:00:00', '09:30:00', 'Poussin-1-A', 'Mhiri Afif', 2, NULL),
(19, '2025-01-28', '08:00:00', '09:30:00', 'Lutin-1-A', 'Kharrat Ramzi', 1, NULL),
(20, '2025-01-28', '09:30:00', '11:00:00', 'Lutin-1-A', 'Kharrat Ramzi', 1, NULL),
(21, '2025-02-03', '09:30:00', '11:00:00', 'Lutin-1-B', 'Kharrat Ramzi', 1, NULL),
(22, '2025-01-20', '09:30:00', '11:00:00', 'Poussin-1-B', 'Mhiri Afif', 2, NULL),
(23, '2025-01-21', '08:00:00', '09:30:00', 'Poussin-1-B', 'Mhiri Afif', 1, NULL),
(25, '2025-01-20', '09:30:00', '11:00:00', 'Lutin-1-A', 'Kharrat Ramzi', 1, NULL),
(29, '2025-01-27', '08:00:00', '09:30:00', 'Poussin-1-B', 'Mhiri Afif', 1, NULL),
(31, '2025-02-03', '08:00:00', '09:30:00', 'Ecole-1-A', 'Missoum Walid', 1, NULL),
(32, '2025-02-03', '12:30:00', '14:00:00', 'Poussin-1-A', 'Mhiri Afif', 1, NULL),
(33, '2025-05-07', '08:00:00', '09:30:00', 'Ecole-1-A', 'Mhiri Afif', 1, NULL);

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
) ;

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
(3, 'manager', '6ee4a469cd4e91053847f5d3fcb61dbcc91e8f0ef10be7748da4c4a1ba382d17', 'directeur_technique'),
(6, 'john.doe', '03ac674216f3e15c761ee1a5e255f067953623c8b388b4459e13f978d7c846f4', 'entraineur'),
(7, 'Zallila.Adam', 'a18ceb2154111dd7e9bdfe59a36ae187ef6880bdbe676fb47ca1bb796f3dcbc1', 'entraineur'),
(8, 'jaber.ons', 'a18ceb2154111dd7e9bdfe59a36ae187ef6880bdbe676fb47ca1bb796f3dcbc1', 'entraineur'),
(9, 'mhiri.afif', 'a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3', 'entraineur'),
(10, 'jebri.amine', 'a18ceb2154111dd7e9bdfe59a36ae187ef6880bdbe676fb47ca1bb796f3dcbc1', 'entraineur'),
(11, 'jegham.anis', 'a18ceb2154111dd7e9bdfe59a36ae187ef6880bdbe676fb47ca1bb796f3dcbc1', 'entraineur'),
(12, 'hdaya.aya', 'a18ceb2154111dd7e9bdfe59a36ae187ef6880bdbe676fb47ca1bb796f3dcbc1', 'entraineur'),
(13, 'gaaloul.ilhem', 'a18ceb2154111dd7e9bdfe59a36ae187ef6880bdbe676fb47ca1bb796f3dcbc1', 'entraineur'),
(14, 'kbaili.nour', 'a18ceb2154111dd7e9bdfe59a36ae187ef6880bdbe676fb47ca1bb796f3dcbc1', 'entraineur'),
(15, 'kharrat.ramzi', 'a18ceb2154111dd7e9bdfe59a36ae187ef6880bdbe676fb47ca1bb796f3dcbc1', 'entraineur'),
(16, 'missoum.walid', 'a18ceb2154111dd7e9bdfe59a36ae187ef6880bdbe676fb47ca1bb796f3dcbc1', 'entraineur'),
(17, 'user', '04f8996da763b7a969b1028ee3007569eaf3a635486ddab211d512c85b9df8fb', 'admin'),
(18, 'aaa.bbb', 'a18ceb2154111dd7e9bdfe59a36ae187ef6880bdbe676fb47ca1bb796f3dcbc1', 'entraineur');

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
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_category` (`category`),
  ADD KEY `idx_date` (`date`),
  ADD KEY `idx_autres_paiements_date` (`date`),
  ADD KEY `idx_autres_paiements_company` (`company_name`),
  ADD KEY `idx_autres_paiements_bank` (`bank_name`);

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
  MODIFY `adherent_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=15;

--
-- AUTO_INCREMENT pour la table `autres_paiements`
--
ALTER TABLE `autres_paiements`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT pour la table `bon_de_recette`
--
ALTER TABLE `bon_de_recette`
  MODIFY `id_bon` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT pour la table `cotisations`
--
ALTER TABLE `cotisations`
  MODIFY `id_cotisation` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=14;

--
-- AUTO_INCREMENT pour la table `depense`
--
ALTER TABLE `depense`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT pour la table `entraineur`
--
ALTER TABLE `entraineur`
  MODIFY `id_entraineur` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=22;

--
-- AUTO_INCREMENT pour la table `groupe`
--
ALTER TABLE `groupe`
  MODIFY `id_groupe` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=21;

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
  MODIFY `id_paiement` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=33;

--
-- AUTO_INCREMENT pour la table `participanttournoi`
--
ALTER TABLE `participanttournoi`
  MODIFY `id_participation` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT pour la table `presence`
--
ALTER TABLE `presence`
  MODIFY `id_presence` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT pour la table `revenu`
--
ALTER TABLE `revenu`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT pour la table `seances`
--
ALTER TABLE `seances`
  MODIFY `seance_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=34;

--
-- AUTO_INCREMENT pour la table `tournois`
--
ALTER TABLE `tournois`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT pour la table `utilisateurs`
--
ALTER TABLE `utilisateurs`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=19;

--
-- Contraintes pour les tables déchargées
--

--
-- Contraintes pour la table `match`
--
ALTER TABLE `match`
  ADD CONSTRAINT `match_ibfk_1` FOREIGN KEY (`id_tournoi`) REFERENCES `tournoi` (`id_tournoi`) ON DELETE CASCADE,
  ADD CONSTRAINT `match_ibfk_2` FOREIGN KEY (`match_suivant`) REFERENCES `match` (`id_match`) ON DELETE SET NULL;

--
-- Contraintes pour la table `participanttournoi`
--
ALTER TABLE `participanttournoi`
  ADD CONSTRAINT `participanttournoi_ibfk_1` FOREIGN KEY (`id_tournoi`) REFERENCES `tournoi` (`id_tournoi`) ON DELETE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
