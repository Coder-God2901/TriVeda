-- CreateTable
CREATE TABLE "PrakritiAssessment" (
    "id" TEXT NOT NULL,
    "patientId" TEXT NOT NULL,
    "answer1" TEXT NOT NULL,
    "answer2" TEXT NOT NULL,
    "answer3" TEXT NOT NULL,
    "answer4" TEXT NOT NULL,
    "answer5" TEXT NOT NULL,
    "answer6" TEXT NOT NULL,
    "answer7" TEXT NOT NULL,
    "answer8" TEXT NOT NULL,
    "vataScore" INTEGER NOT NULL,
    "pittaScore" INTEGER NOT NULL,
    "kaphaScore" INTEGER NOT NULL,
    "primaryDosha" TEXT NOT NULL,
    "timeSpentSec" INTEGER,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "PrakritiAssessment_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE INDEX "PrakritiAssessment_patientId_createdAt_idx" ON "PrakritiAssessment"("patientId", "createdAt");

-- AddForeignKey
ALTER TABLE "PrakritiAssessment" ADD CONSTRAINT "PrakritiAssessment_patientId_fkey" FOREIGN KEY ("patientId") REFERENCES "Patient"("id") ON DELETE CASCADE ON UPDATE CASCADE;
