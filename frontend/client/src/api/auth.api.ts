import { apiClient } from './client';

export const authApi = {
    staffLogin: async (credentials: any) => {
        return apiClient.post('/auth/staff/login', credentials);
    },
    patientLogin: async (credentials: any) => {
        return apiClient.post('/auth/patient/login', credentials);
    },
    patientRegister: async (payload: any) => {
        return apiClient.post('/auth/patient/register', payload);
    },
    // Admin function to create doctors
    createDoctor: async (doctorData: any) => {
        return apiClient.post('/admin/create-doctor', doctorData);
    },
    getDoctors: async (hospitalId?: string) => {
        const url = hospitalId
            ? `/admin/doctors?hospitalId=${encodeURIComponent(hospitalId)}`
            : '/admin/doctors';
        return apiClient.get(url);
    },
    getPatients: async () => {
        return apiClient.get('/admin/patients');
    },
    deleteDoctor: async (doctorId: string) => {
        return apiClient.delete(`/admin/doctors/${doctorId}`);
    },
    deletePatient: async (patientId: string) => {
        return apiClient.delete(`/admin/patients/${patientId}`);
    },
    // Fetch available departments
    getDepartments: async () => {
        return apiClient.get('/admin/departments');
    }
};