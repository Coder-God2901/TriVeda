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
};
