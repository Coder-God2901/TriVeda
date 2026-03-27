-- AlterEnum
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1
    FROM pg_enum e
    JOIN pg_type t ON t.oid = e.enumtypid
    WHERE t.typname = 'AppointmentStatus' AND e.enumlabel = 'LIVE'
  ) THEN
    ALTER TYPE "AppointmentStatus" ADD VALUE 'LIVE';
  END IF;
END
$$;
