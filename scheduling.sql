-- phpMyAdmin SQL Dump
-- version 5.2.0
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Jan 18, 2023 at 11:59 AM
-- Server version: 10.4.27-MariaDB
-- PHP Version: 8.1.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `scheduling`
--

-- --------------------------------------------------------

--
-- Table structure for table `admin`
--

CREATE TABLE `admin` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `admin`
--

INSERT INTO `admin` (`id`, `user_id`) VALUES
(1, 1);

-- --------------------------------------------------------

--
-- Table structure for table `appointment`
--

CREATE TABLE `appointment` (
  `id` int(11) NOT NULL,
  `field_of_work` int(11) NOT NULL,
  `client_id` int(11) NOT NULL,
  `date` date NOT NULL,
  `time` enum('morning','afternoon') NOT NULL,
  `description` text NOT NULL,
  `estimated_time` int(11) DEFAULT NULL,
  `materials_status` enum('available','unavailable') NOT NULL,
  `status` enum('pending','approved','rejected','done','cancelled') NOT NULL DEFAULT 'pending',
  `worker` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `appointment`
--

INSERT INTO `appointment` (`id`, `field_of_work`, `client_id`, `date`, `time`, `description`, `estimated_time`, `materials_status`, `status`, `worker`) VALUES
(8, 1, 2, '2023-01-15', 'afternoon', 'asdqwe', NULL, 'available', 'pending', 2),
(9, 3, 2, '2023-01-20', 'morning', 'Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry\'s standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum.', 5, 'available', 'pending', 3),
(10, 2, 1, '2023-01-13', 'afternoon', 'asdqwe', 5, 'unavailable', 'pending', 1),
(11, 1, 1, '2023-01-16', 'morning', 'asdqwe', NULL, 'available', 'pending', 2),
(12, 1, 2, '2023-01-18', 'afternoon', 'asdqwe', NULL, 'available', 'pending', 2),
(13, 1, 1, '2023-01-18', 'morning', 'asdqwe', NULL, 'available', 'pending', 2);

-- --------------------------------------------------------

--
-- Table structure for table `client`
--

CREATE TABLE `client` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `office` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `client`
--

INSERT INTO `client` (`id`, `user_id`, `office`) VALUES
(1, 2, 'CAC'),
(2, 3, 'CS');

-- --------------------------------------------------------

--
-- Table structure for table `field_of_work`
--

CREATE TABLE `field_of_work` (
  `id` int(11) NOT NULL,
  `name` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `field_of_work`
--

INSERT INTO `field_of_work` (`id`, `name`) VALUES
(1, 'Art & Science'),
(2, 'Computer Services'),
(3, 'Carpentry'),
(4, 'Electrical'),
(5, 'Painting'),
(6, 'Masonry'),
(7, 'Plumbing'),
(8, 'Welding'),
(9, 'Landscaping'),
(10, 'Utility'),
(11, 'Brush Cutter Operator'),
(12, 'Refrigeration & Air-conditioning');

-- --------------------------------------------------------

--
-- Table structure for table `notification`
--

CREATE TABLE `notification` (
  `id` int(11) NOT NULL,
  `appointment_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `status` enum('read','unread') NOT NULL DEFAULT 'unread'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `user`
--

CREATE TABLE `user` (
  `id` int(11) NOT NULL,
  `role` enum('admin','client') NOT NULL,
  `email` varchar(255) NOT NULL,
  `password` varchar(255) NOT NULL,
  `first_name` varchar(255) NOT NULL,
  `last_name` varchar(255) NOT NULL,
  `gender` enum('male','female') NOT NULL,
  `birth_date` date NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `user`
--

INSERT INTO `user` (`id`, `role`, `email`, `password`, `first_name`, `last_name`, `gender`, `birth_date`) VALUES
(1, 'admin', 'admin@email.com', '$5$rounds=535000$YHSF5ZBwIaPWfU5O$8NUrW6rXoW42uYi89NdTzfvPp55Y.rulRDX4yvdmfv/', 'admin1', 'admin1', 'female', '2023-01-12'),
(2, 'client', 'client@email.com', '$5$rounds=535000$/vTG6..47G1awTBO$jvV/PNz4L3BMPBi.4Yf1AEddDS9PdnY38qiytk0W.l9', 'client1', 'client1', 'female', '2023-02-01'),
(3, 'client', 'client2@email.com', '$5$rounds=535000$0GFEHYxSWAaRm4t2$7Fprp/w1Ly4tW2EXz7X0ATS8lOAk2m/diGqKdi7UcX/', 'client2', 'client2', 'female', '2023-01-06');

-- --------------------------------------------------------

--
-- Table structure for table `worker`
--

CREATE TABLE `worker` (
  `id` int(11) NOT NULL,
  `last_name` varchar(255) NOT NULL,
  `first_name` varchar(255) NOT NULL,
  `field_of_work` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `worker`
--

INSERT INTO `worker` (`id`, `last_name`, `first_name`, `field_of_work`) VALUES
(1, 'dela cruz', 'juan', 2),
(2, 'Wick', 'John', 1),
(3, 'Potter', 'Harry', 3),
(4, 'Doll', 'Barbie', 9);

--
-- Indexes for dumped tables
--

--
-- Indexes for table `admin`
--
ALTER TABLE `admin`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `appointment`
--
ALTER TABLE `appointment`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `client`
--
ALTER TABLE `client`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `field_of_work`
--
ALTER TABLE `field_of_work`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `notification`
--
ALTER TABLE `notification`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `user`
--
ALTER TABLE `user`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `worker`
--
ALTER TABLE `worker`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `admin`
--
ALTER TABLE `admin`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `appointment`
--
ALTER TABLE `appointment`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=14;

--
-- AUTO_INCREMENT for table `client`
--
ALTER TABLE `client`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT for table `field_of_work`
--
ALTER TABLE `field_of_work`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=13;

--
-- AUTO_INCREMENT for table `notification`
--
ALTER TABLE `notification`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=10;

--
-- AUTO_INCREMENT for table `user`
--
ALTER TABLE `user`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT for table `worker`
--
ALTER TABLE `worker`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
