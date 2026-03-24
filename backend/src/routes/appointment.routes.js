import { Router } from "express";
import {
  bookAppointment,
  diagnoseSymptoms,
  getAvailableSlots,
  saveDoctorPlan,
  getDoctorAppointments,
  getPatientAppointments,
  getPatientDashboardData,
  savePrakritiAssessment,
  getPatientPrakritiAssessments,
} from "../controllers/appointment.controller.js";
import { getDoctorPatients } from "../controllers/doctor.controller.js";

const router = Router();

router.post("/diagnose", diagnoseSymptoms);
router.get("/slots", getAvailableSlots);
router.post("/book", bookAppointment);
router.get("/:appointmentId/plan", saveDoctorPlan);
router.get("/doctor/:doctorId/patients", getDoctorPatients);
router.get("/doctor/:doctorId", getDoctorAppointments);
router.get("/patient/:patientId", getPatientAppointments);
router.get("/patient/:patientId/dashboard", getPatientDashboardData);
router.post("/patient/:patientId/prakriti-assessment", savePrakritiAssessment);
router.get("/patient/:patientId/prakriti-assessment", getPatientPrakritiAssessments);

export default router;
