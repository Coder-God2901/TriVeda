import { apiClient } from "./client";

export const appointmentApi = {
  // 1. Smart Triage (NLP Diagnosis)
  diagnoseSymptoms: async (data: {
    problemDescription?: string;
    providedSymptoms?: string[];
    providedSeverity?: string | null;
    providedDuration?: string | null;
  }) => {
    return apiClient.post("/appointments/diagnose", data);
  },

  // 2. Fetch Available Time Slots
  getAvailableSlots: async (
    departmentId: string,
    date: string,
    doctorId?: string,
  ) => {
    let url = `/appointments/slots?departmentId=${departmentId}&date=${date}`;
    if (doctorId) url += `&doctorId=${doctorId}`; // Hybrid Flow bypass
    return apiClient.get(url);
  },

  // 3. Book the Appointment
  bookAppointment: async (bookingPayload: any) => {
    return apiClient.post("/appointments/book", bookingPayload);
  },

  // 4. Fetch Doctor's Dashboard Appointments
  getDoctorAppointments: async (doctorId: string) => {
    return apiClient.get(`/appointments/doctor/${doctorId}`);
  },

  // 5. Save the Doctor's Ayurvedic Diet/Routine Plan
  saveDoctorPlan: async (appointmentId: string, planData: any) => {
    return apiClient.put(`/appointments/${appointmentId}/plan`, planData);
  },
  
  // 6. Fetch Patient's Appointments
  getPatientAppointments: async (patientId: string) => {
        return apiClient.get(`/appointments/patient/${patientId}`);
    },

  // 7. Fetch Patient Dashboard Data (profile + appointments + plans)
  getPatientDashboard: async (patientId: string) => {
    return apiClient.get(`/appointments/patient/${patientId}/dashboard`);
  },

  // 8. Save Prakriti Assessment Results
  savePrakritiAssessment: async (patientId: string, payload: any) => {
    return apiClient.post(
      `/appointments/patient/${patientId}/prakriti-assessment`,
      payload,
    );
  }
};
