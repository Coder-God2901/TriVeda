/*
  Warnings:

  - You are about to drop the column `rescheduledToId` on the `Appointment` table. All the data in the column will be lost.
  - You are about to drop the column `transactionId` on the `Appointment` table. All the data in the column will be lost.
  - The `paymentStatus` column on the `Appointment` table would be dropped and recreated. This will lead to data loss if there is data in the column.
  - You are about to drop the column `createdAt` on the `Department` table. All the data in the column will be lost.
  - You are about to drop the column `userId` on the `DoctorProfile` table. All the data in the column will be lost.
  - You are about to drop the column `createdAt` on the `Hospital` table. All the data in the column will be lost.
  - You are about to drop the `PatientProfile` table. If the table is not empty, all the data it contains will be lost.
  - You are about to drop the `User` table. If the table is not empty, all the data it contains will be lost.
  - A unique constraint covering the columns `[staffId]` on the table `DoctorProfile` will be added. If there are existing duplicate values, this will fail.
  - Added the required column `staffId` to the `DoctorProfile` table without a default value. This is not possible if the table is not empty.
  - Made the column `experienceYrs` on table `DoctorProfile` required. This step will fail if there are existing NULL values in that column.

*/
-- CreateEnum
CREATE TYPE "StaffRole" AS ENUM ('ADMIN', 'DOCTOR', 'RECEPTIONIST', 'PHARMACIST', 'NURSE', 'THERAPIST', 'BILLING');

-- DropForeignKey
ALTER TABLE "Appointment" DROP CONSTRAINT "Appointment_doctorId_fkey";

-- DropForeignKey
ALTER TABLE "Appointment" DROP CONSTRAINT "Appointment_patientId_fkey";

-- DropForeignKey
ALTER TABLE "Appointment" DROP CONSTRAINT "Appointment_rescheduledToId_fkey";

-- DropForeignKey
ALTER TABLE "DoctorProfile" DROP CONSTRAINT "DoctorProfile_userId_fkey";

-- DropForeignKey
ALTER TABLE "PatientProfile" DROP CONSTRAINT "PatientProfile_userId_fkey";

-- DropForeignKey
ALTER TABLE "User" DROP CONSTRAINT "User_hospitalId_fkey";

-- DropIndex
DROP INDEX "Appointment_rescheduledToId_key";

-- DropIndex
DROP INDEX "Appointment_transactionId_key";

-- DropIndex
DROP INDEX "Department_name_key";

-- DropIndex
DROP INDEX "DoctorProfile_userId_key";

-- AlterTable
ALTER TABLE "Appointment" DROP COLUMN "rescheduledToId",
DROP COLUMN "transactionId",
DROP COLUMN "paymentStatus",
ADD COLUMN     "paymentStatus" TEXT NOT NULL DEFAULT 'PENDING';

-- AlterTable
ALTER TABLE "Department" DROP COLUMN "createdAt",
ALTER COLUMN "description" DROP NOT NULL;

-- AlterTable
ALTER TABLE "DoctorProfile" DROP COLUMN "userId",
ADD COLUMN     "staffId" TEXT NOT NULL,
ALTER COLUMN "experienceYrs" SET NOT NULL;

-- AlterTable
ALTER TABLE "Hospital" DROP COLUMN "createdAt",
ADD COLUMN     "address" TEXT;

-- DropTable
DROP TABLE "PatientProfile";

-- DropTable
DROP TABLE "User";

-- DropEnum
DROP TYPE "PaymentStatus";

-- DropEnum
DROP TYPE "Role";

-- CreateTable
CREATE TABLE "Patient" (
    "id" TEXT NOT NULL,
    "email" TEXT,
    "phoneNumber" TEXT,
    "password" TEXT,
    "name" TEXT NOT NULL,
    "isAppRegistered" BOOLEAN NOT NULL DEFAULT false,
    "age" INTEGER,
    "gender" TEXT,
    "bloodGroup" TEXT,
    "prakriti" TEXT,
    "vikriti" TEXT,
    "vataScore" INTEGER,
    "pittaScore" INTEGER,
    "kaphaScore" INTEGER,
    "allergies" TEXT[] DEFAULT ARRAY[]::TEXT[],
    "dietaryPref" TEXT,
    "clinicalData" JSONB,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "Patient_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "HospitalStaff" (
    "id" TEXT NOT NULL,
    "email" TEXT NOT NULL,
    "password" TEXT NOT NULL,
    "name" TEXT NOT NULL,
    "role" "StaffRole" NOT NULL,
    "hospitalId" TEXT NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "HospitalStaff_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "TherapistProfile" (
    "id" TEXT NOT NULL,
    "staffId" TEXT NOT NULL,
    "certifications" TEXT[] DEFAULT ARRAY[]::TEXT[],

    CONSTRAINT "TherapistProfile_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE UNIQUE INDEX "Patient_email_key" ON "Patient"("email");

-- CreateIndex
CREATE UNIQUE INDEX "Patient_phoneNumber_key" ON "Patient"("phoneNumber");

-- CreateIndex
CREATE UNIQUE INDEX "HospitalStaff_email_key" ON "HospitalStaff"("email");

-- CreateIndex
CREATE UNIQUE INDEX "TherapistProfile_staffId_key" ON "TherapistProfile"("staffId");

-- CreateIndex
CREATE UNIQUE INDEX "DoctorProfile_staffId_key" ON "DoctorProfile"("staffId");

-- AddForeignKey
ALTER TABLE "HospitalStaff" ADD CONSTRAINT "HospitalStaff_hospitalId_fkey" FOREIGN KEY ("hospitalId") REFERENCES "Hospital"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "DoctorProfile" ADD CONSTRAINT "DoctorProfile_staffId_fkey" FOREIGN KEY ("staffId") REFERENCES "HospitalStaff"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "TherapistProfile" ADD CONSTRAINT "TherapistProfile_staffId_fkey" FOREIGN KEY ("staffId") REFERENCES "HospitalStaff"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Appointment" ADD CONSTRAINT "Appointment_patientId_fkey" FOREIGN KEY ("patientId") REFERENCES "Patient"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Appointment" ADD CONSTRAINT "Appointment_doctorId_fkey" FOREIGN KEY ("doctorId") REFERENCES "HospitalStaff"("id") ON DELETE RESTRICT ON UPDATE CASCADE;
