import { prisma } from '../db/config.js';
import ApiError from '../utils/ApiError.js';
import ApiResponse from '../utils/ApiResponse.js';
import asyncHandler from '../utils/asyncHandler.js';

/**
 * Get all unique patients assigned to a doctor with aggregated details
 * Includes appointment history, compliance scores, risk assessment
 */
export const getDoctorPatients = asyncHandler(async (req, res) => {
    const { doctorId } = req.params;

    if (!doctorId) {
        throw new ApiError(400, 'Doctor ID is required.');
    }

    // Verify doctor exists
    const doctor = await prisma.hospitalStaff.findUnique({
        where: { id: doctorId },
        select: { id: true, role: true },
    });

    if (!doctor || doctor.role !== 'DOCTOR') {
        throw new ApiError(404, 'Doctor not found.');
    }

    // Get all appointments for this doctor
    const appointments = await prisma.appointment.findMany({
        where: { doctorId, status: { not: 'CANCELLED' } },
        orderBy: { scheduledAt: 'desc' },
        include: {
            patient: {
                select: {
                    id: true,
                    name: true,
                    email: true,
                    phoneNumber: true,
                    age: true,
                    gender: true,
                    prakriti: true,
                    vikriti: true,
                    dietaryPref: true,
                    bloodGroup: true,
                    allergies: true,
                    clinicalData: true,
                    profileImageMimeType: true,
                },
            },
        },
    });

    // Build unique patient map with aggregated data
    const patientMap = new Map();

    appointments.forEach((appointment) => {
        const patient = appointment.patient;
        if (!patientMap.has(patient.id)) {
            // Extract clinical data
            const clinicalData =
                patient.clinicalData && typeof patient.clinicalData === 'object'
                    ? patient.clinicalData
                    : {};

            // Calculate compliance from appointments
            const patientAppointments = appointments.filter(
                (apt) => apt.patient.id === patient.id
            );
            const completedCount = patientAppointments.filter(
                (apt) => apt.status === 'COMPLETED'
            ).length;
            const compliance =
                patientAppointments.length > 0
                    ? Math.round((completedCount / patientAppointments.length) * 100)
                    : 0;

            // Determine status and priority based on patterns
            let status = 'active';
            let priority = 'low';
            let riskScore = 1;

            if (compliance < 60) {
                status = 'needs-attention';
                priority = 'high';
                riskScore = 4;
            } else if (compliance < 75) {
                priority = 'medium';
                riskScore = 2;
            }

            // Get last visit and next appointment
            const sortedByDate = [...patientAppointments].sort(
                (a, b) => new Date(b.scheduledAt).getTime() - new Date(a.scheduledAt).getTime()
            );
            const lastVisit = sortedByDate
                .find((apt) => apt.status === 'COMPLETED')
                ?.scheduledAt || sortedByDate[0]?.scheduledAt;
            const nextAppointment = sortedByDate
                .find((apt) =>
                    new Date(apt.scheduledAt) > new Date() && apt.status !== 'CANCELLED'
                )
                ?.scheduledAt || (sortedByDate[0]?.scheduledAt || new Date());

            patientMap.set(patient.id, {
                id: patient.id,
                name: patient.name,
                age: patient.age || 0,
                gender: patient.gender || 'Not specified',
                prakriti: patient.prakriti || 'Not Assessed',
                vikriti: patient.vikriti || 'Not specified',
                email: patient.email,
                phone: patient.phoneNumber || '-',
                bloodGroup: patient.bloodGroup || 'Not specified',
                dietaryPref: patient.dietaryPref || 'Not specified',
                allergies: Array.isArray(patient.allergies) ? patient.allergies : [],
                lastVisit: lastVisit
                    ? new Date(lastVisit).toISOString().split('T')[0]
                    : '-',
                nextAppointment: nextAppointment
                    ? new Date(nextAppointment).toISOString().split('T')[0]
                    : '-',
                compliance,
                status,
                priority,
                riskScore,
                avatar: patient.profileImageMimeType
                    ? `/api/profile/patient/${patient.id}/image`
                    : null,
                issues: Array.isArray(clinicalData.healthGoals)
                    ? clinicalData.healthGoals
                    : [],
                vitalSigns:
                    clinicalData.weight || clinicalData.height
                        ? {
                              bp: clinicalData.bloodPressure || '-',
                              pulse: clinicalData.pulse || 0,
                              weight: clinicalData.weight
                                  ? `${clinicalData.weight}kg`
                                  : '-',
                              temp: clinicalData.temperature || '-',
                          }
                        : { bp: '-', pulse: 0, weight: '-', temp: '-' },
                medications: Array.isArray(clinicalData.medications)
                    ? clinicalData.medications
                    : [],
                starred: false,
                appointmentCount: patientAppointments.length,
            });
        }
    });

    const patients = Array.from(patientMap.values());

    return res
        .status(200)
        .json(new ApiResponse(200, patients, 'Doctor patients fetched successfully.'));
});
