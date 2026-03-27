-- AlterTable
ALTER TABLE "Appointment"
ADD COLUMN IF NOT EXISTS "diagnosis" JSONB;

-- CreateTable
CREATE TABLE IF NOT EXISTS "TreatmentPlan" (
  "id" TEXT NOT NULL,
  "appointmentId" TEXT NOT NULL,
  "patientId" TEXT NOT NULL,
  "doctorId" TEXT NOT NULL,
  "doctorNotes" TEXT,
  "diagnosis" JSONB,
  "dietChart" JSONB,
  "routinePlan" JSONB,
  "isCompleted" BOOLEAN NOT NULL DEFAULT false,
  "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "updatedAt" TIMESTAMP(3) NOT NULL,
  CONSTRAINT "TreatmentPlan_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE IF NOT EXISTS "TreatmentMedication" (
  "id" TEXT NOT NULL,
  "treatmentPlanId" TEXT NOT NULL,
  "name" TEXT NOT NULL,
  "dosage" TEXT,
  "timing" TEXT,
  "medicineType" TEXT,
  "durationDays" INTEGER,
  "doctorNotes" TEXT,
  "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "updatedAt" TIMESTAMP(3) NOT NULL,
  CONSTRAINT "TreatmentMedication_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE UNIQUE INDEX IF NOT EXISTS "TreatmentPlan_appointmentId_key" ON "TreatmentPlan"("appointmentId");
CREATE INDEX IF NOT EXISTS "TreatmentPlan_patientId_createdAt_idx" ON "TreatmentPlan"("patientId", "createdAt");
CREATE INDEX IF NOT EXISTS "TreatmentPlan_doctorId_createdAt_idx" ON "TreatmentPlan"("doctorId", "createdAt");
CREATE INDEX IF NOT EXISTS "TreatmentMedication_treatmentPlanId_createdAt_idx" ON "TreatmentMedication"("treatmentPlanId", "createdAt");

-- AddForeignKey
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1
    FROM pg_constraint
    WHERE conname = 'TreatmentPlan_appointmentId_fkey'
  ) THEN
    ALTER TABLE "TreatmentPlan"
    ADD CONSTRAINT "TreatmentPlan_appointmentId_fkey"
    FOREIGN KEY ("appointmentId") REFERENCES "Appointment"("id") ON DELETE CASCADE ON UPDATE CASCADE;
  END IF;
END
$$;

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1
    FROM pg_constraint
    WHERE conname = 'TreatmentMedication_treatmentPlanId_fkey'
  ) THEN
    ALTER TABLE "TreatmentMedication"
    ADD CONSTRAINT "TreatmentMedication_treatmentPlanId_fkey"
    FOREIGN KEY ("treatmentPlanId") REFERENCES "TreatmentPlan"("id") ON DELETE CASCADE ON UPDATE CASCADE;
  END IF;
END
$$;
