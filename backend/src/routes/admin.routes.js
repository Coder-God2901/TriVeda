import { Router } from "express";
import {
	createDoctor,
	getDepartments,
	getDoctors,
	getPatients,
	deleteDoctor,
	deletePatient,
} from "../controllers/admin.controller.js";

const router = Router();
router.get("/departments", getDepartments);
router.get("/doctors", getDoctors);
router.get("/patients", getPatients);
router.post("/create-doctor", createDoctor);
router.delete("/doctors/:doctorId", deleteDoctor);
router.delete("/patients/:patientId", deletePatient);
export default router;