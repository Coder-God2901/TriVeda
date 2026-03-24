import React, { useMemo, useState } from "react";
import {
  Activity,
  Calendar,
  CheckCircle,
  ChevronRight,
  Clock,
  Download,
  FileText,
  Pill,
  Stethoscope,
  User,
  Video,
  MapPin,
  AlertCircle,
} from "lucide-react";
import {
  AppointmentBooking,
  DoctorCategory,
  categoryLabelMap,
  createBookingId,
  downloadAppointmentPdf,
  getStoredAppointments,
  inferDoctorCategory,
  saveStoredAppointment,
} from "@/lib/appointment-booking";

type DoctorProfile = {
  id: number;
  name: string;
  department: DoctorCategory;
  experience: number;
  clinic: string;
  availability: Record<string, string[]>;
};

const doctorPool: DoctorProfile[] = [
  {
    id: 1,
    name: "Dr. Meera Kulkarni",
    department: "dentist",
    experience: 11,
    clinic: "TriVeda Dental & Oral Care",
    availability: { Monday: ["09:00", "11:00", "16:00"], Wednesday: ["10:00", "14:00"], Friday: ["09:30", "15:00"] },
  },
  {
    id: 2,
    name: "Dr. Arjun Nair",
    department: "dermatology",
    experience: 13,
    clinic: "TriVeda Skin Wellness",
    availability: { Tuesday: ["10:00", "12:00", "17:00"], Thursday: ["09:30", "13:00"], Saturday: ["11:30", "16:30"] },
  },
  {
    id: 3,
    name: "Dr. Kavita Rao",
    department: "cardiology",
    experience: 18,
    clinic: "TriVeda Cardio Care",
    availability: { Monday: ["10:00", "12:00"], Wednesday: ["09:30", "15:00"], Friday: ["11:00", "14:30"] },
  },
  {
    id: 4,
    name: "Dr. Suresh Iyer",
    department: "orthopedics",
    experience: 16,
    clinic: "TriVeda Joint & Mobility Center",
    availability: { Tuesday: ["09:00", "11:00", "15:30"], Thursday: ["10:30", "13:30"], Saturday: ["09:30", "12:30"] },
  },
  {
    id: 5,
    name: "Dr. Ayesha Khan",
    department: "gastroenterology",
    experience: 14,
    clinic: "TriVeda Digestive Health",
    availability: { Monday: ["08:30", "13:00"], Wednesday: ["11:00", "16:30"], Friday: ["10:30", "14:00"] },
  },
  {
    id: 6,
    name: "Dr. Rohit Sharma",
    department: "ent",
    experience: 12,
    clinic: "TriVeda ENT Specialty",
    availability: { Tuesday: ["09:30", "12:00", "17:00"], Thursday: ["11:00", "15:30"], Saturday: ["10:00", "14:30"] },
  },
  {
    id: 7,
    name: "Dr. Neha Verma",
    department: "general",
    experience: 10,
    clinic: "TriVeda General Medicine",
    availability: {
      Monday: ["09:00", "10:00", "11:00", "15:00"],
      Tuesday: ["09:30", "12:00", "16:00"],
      Wednesday: ["10:30", "14:30"],
      Thursday: ["09:00", "13:00", "17:00"],
      Friday: ["11:30", "16:30"],
    },
  },
];

function formatTimeLabel(time24: string) {
  const [h, m] = time24.split(":").map(Number);
  const period = h >= 12 ? "PM" : "AM";
  const hour = h % 12 === 0 ? 12 : h % 12;
  return `${hour}:${String(m).padStart(2, "0")} ${period}`;
}

function toDateInputValue(date: Date) {
  const y = date.getFullYear();
  const m = String(date.getMonth() + 1).padStart(2, "0");
  const d = String(date.getDate()).padStart(2, "0");
  return `${y}-${m}-${d}`;
}

function PatientAppointments() {
  const [step, setStep] = useState<1 | 2 | 3 | 4 | 5>(1);

  const [diagnosis, setDiagnosis] = useState("");
  const [symptoms, setSymptoms] = useState("");
  const [duration, setDuration] = useState("");
  const [severity, setSeverity] = useState<"mild" | "moderate" | "severe">("moderate");

  const [doctorCategory, setDoctorCategory] = useState<DoctorCategory | "">("");
  const [selectedDoctorId, setSelectedDoctorId] = useState<number | null>(null);
  const [autoAssignedDoctorId, setAutoAssignedDoctorId] = useState<number | null>(null);
  const [selectedDate, setSelectedDate] = useState("");
  const [selectedTime, setSelectedTime] = useState("");
  const [calendarMonth, setCalendarMonth] = useState(() => {
    const now = new Date();
    return new Date(now.getFullYear(), now.getMonth(), 1);
  });
  const [consultationMode, setConsultationMode] = useState<"clinic" | "video">("clinic");

  const [additionalNotes, setAdditionalNotes] = useState("");

  const [bookings, setBookings] = useState<AppointmentBooking[]>(() => getStoredAppointments());
  const [confirmedBooking, setConfirmedBooking] = useState<AppointmentBooking | null>(null);

  const dayName = useMemo(() => {
    if (!selectedDate) return "";
    return new Date(selectedDate).toLocaleDateString("en-US", { weekday: "long" });
  }, [selectedDate]);

  const categoryDoctors = useMemo(() => {
    if (!doctorCategory) return [];
    return doctorPool.filter((doctor) => doctor.department === doctorCategory);
  }, [doctorCategory]);

  const selectedDoctor = useMemo(() => {
    const doctorId = selectedDoctorId ?? autoAssignedDoctorId;
    if (!doctorId) return null;
    return doctorPool.find((doctor) => doctor.id === doctorId) || null;
  }, [selectedDoctorId, autoAssignedDoctorId]);

  const availableSlots = useMemo(() => {
    if (!selectedDoctor || !dayName) return [];
    return [...(selectedDoctor.availability[dayName] || [])].sort();
  }, [selectedDoctor, dayName]);

  const calendarCells = useMemo(() => {
    const year = calendarMonth.getFullYear();
    const month = calendarMonth.getMonth();
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    const startOffset = firstDay.getDay();

    const cells: Array<Date | null> = [];
    for (let index = 0; index < startOffset; index += 1) cells.push(null);
    for (let day = 1; day <= lastDay.getDate(); day += 1) {
      cells.push(new Date(year, month, day));
    }

    return cells;
  }, [calendarMonth]);

  const getSlotsForDate = (date: Date) => {
    if (!selectedDoctor) return [];
    const weekday = date.toLocaleDateString("en-US", { weekday: "long" });
    return selectedDoctor.availability[weekday] || [];
  };

  const isDateSelectable = (date: Date) => {
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    if (date < today) return false;
    return getSlotsForDate(date).length > 0;
  };

  const stepTitles: Record<number, string> = {
    1: "Diagnosis",
    2: "Doctor Category",
    3: "Available Time Slots",
    4: "Assigning Doctor",
    5: "Downloadable PDF",
  };

  const detectCategory = () => {
    if (!diagnosis.trim() && !symptoms.trim()) return;
    const inferred = inferDoctorCategory(`${diagnosis} ${symptoms}`);
    setDoctorCategory(inferred);
    setSelectedDoctorId(null);
    setAutoAssignedDoctorId(null);
    setSelectedDate("");
    setSelectedTime("");
    setStep(2);
  };

  const handleAutoAssignDoctor = () => {
    if (!doctorCategory) return;

    const candidates = doctorPool.filter((doctor) => doctor.department === doctorCategory);
    if (candidates.length === 0) return;

    const sorted = [...candidates].sort((a, b) => b.experience - a.experience);
    const assigned =
      severity === "severe"
        ? sorted[0]
        : severity === "mild"
          ? sorted[sorted.length - 1] || sorted[0]
          : sorted[Math.floor(sorted.length / 2)] || sorted[0];

    setAutoAssignedDoctorId(assigned.id);
    setSelectedDoctorId(null);
    setSelectedDate("");
    setSelectedTime("");
    setStep(3);
  };

  const handleSelectDoctor = (doctorId: number) => {
    setSelectedDoctorId(doctorId);
    setAutoAssignedDoctorId(null);
    setSelectedDate("");
    setSelectedTime("");
  };

  const handleConfirmBooking = () => {
    if (!doctorCategory || !selectedDate || !selectedTime || !selectedDoctor) return;

    const booking: AppointmentBooking = {
      id: String(Date.now()),
      bookingId: createBookingId(),
      createdAt: new Date().toISOString(),
      diagnosis,
      symptoms,
      duration,
      severity,
      doctorCategory,
      selectedDate,
      selectedTime: formatTimeLabel(selectedTime),
      consultationMode,
      patientName: "Patient User",
      patientAge: "-",
      patientGender: "-",
      currentMedications: "",
      allergies: "",
      medicalHistory: "",
      additionalNotes,
      assignedDoctor: {
        id: selectedDoctor.id,
        name: selectedDoctor.name,
        department: categoryLabelMap[selectedDoctor.department],
        experience: selectedDoctor.experience,
        clinic: selectedDoctor.clinic,
      },
      status: "confirmed",
    };

    saveStoredAppointment(booking);
    setConfirmedBooking(booking);
    setBookings(getStoredAppointments());
    setStep(5);
  };

  return (
    <div className="min-h-screen bg-background text-foreground">
      <div className="max-w-7xl mx-auto px-4 py-4 sm:py-6 lg:py-8">
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-emerald-500 to-[#10B981] rounded-full shadow-lg mb-4">
            <Stethoscope className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-3xl sm:text-4xl font-bold bg-gradient-to-r from-emerald-600 to-[#10B981] bg-clip-text text-transparent mb-2 leading-tight break-words">
            Appointment Booking Flow
          </h1>
          <p className="text-gray-600 text-sm sm:text-base max-w-3xl mx-auto leading-relaxed">
            Diagnosis to AI doctor assignment, with a downloadable PDF summary for every confirmed booking.
          </p>
        </div>

        <div className="mb-8">
          <div className="flex flex-wrap items-center justify-start sm:justify-center gap-2 sm:gap-3">
            {[1, 2, 3, 4, 5].map((current) => (
              <React.Fragment key={current}>
                <div className="flex items-center gap-2">
                  <div
                    className={`w-9 h-9 rounded-full flex items-center justify-center text-sm font-semibold ${
                      step >= current ? "bg-emerald-500 text-white" : "bg-gray-200 text-gray-600"
                    }`}
                  >
                    {current}
                  </div>
                  <span className={`text-xs sm:text-sm font-medium ${step >= current ? "text-emerald-700" : "text-gray-500"}`}>
                    {stepTitles[current]}
                  </span>
                </div>
                {current < 5 && <ChevronRight className="hidden sm:block w-4 h-4 text-gray-400" />}
              </React.Fragment>
            ))}
          </div>
        </div>

        <div className="grid lg:grid-cols-3 gap-4 sm:gap-6 lg:gap-8">
          <div className="lg:col-span-2">
            <div className="bg-white rounded-2xl shadow-xl border border-gray-200 overflow-hidden">
              <div className="bg-gradient-to-r from-emerald-500 to-[#10B981] p-4 sm:p-6">
                <h2 className="text-xl sm:text-2xl font-bold text-white leading-tight break-words">Step {step}: {stepTitles[step]}</h2>
              </div>

              <div className="p-4 sm:p-6 space-y-6">
                {step === 1 && (
                  <>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Describe your problem in detail *</label>
                      <textarea
                        value={diagnosis}
                        onChange={(e) => setDiagnosis(e.target.value)}
                        rows={5}
                        placeholder="Explain all symptoms, triggers, and concerns..."
                        className="w-full p-3 border border-gray-200 rounded-lg focus:ring-2 focus:ring-emerald-500"
                      />
                    </div>
                    <div className="grid md:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">Symptoms</label>
                        <textarea
                          value={symptoms}
                          onChange={(e) => setSymptoms(e.target.value)}
                          rows={4}
                          placeholder="e.g. tooth pain, gum swelling"
                          className="w-full p-3 border border-gray-200 rounded-lg focus:ring-2 focus:ring-emerald-500"
                        />
                      </div>
                      <div className="space-y-4">
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-2">Problem duration</label>
                          <input
                            value={duration}
                            onChange={(e) => setDuration(e.target.value)}
                            placeholder="e.g. 2 weeks"
                            className="w-full p-3 border border-gray-200 rounded-lg focus:ring-2 focus:ring-emerald-500"
                          />
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-2">Severity</label>
                          <select
                            value={severity}
                            onChange={(e) => setSeverity(e.target.value as "mild" | "moderate" | "severe")}
                            className="w-full p-3 border border-gray-200 rounded-lg focus:ring-2 focus:ring-emerald-500"
                          >
                            <option value="mild">Mild</option>
                            <option value="moderate">Moderate</option>
                            <option value="severe">Severe</option>
                          </select>
                        </div>
                      </div>
                    </div>
                    <button
                      type="button"
                      onClick={detectCategory}
                      disabled={!diagnosis.trim()}
                      className="w-full py-3 bg-gradient-to-r from-emerald-500 to-[#10B981] text-white rounded-lg font-semibold disabled:opacity-50"
                    >
                      Determine Doctor Category
                    </button>
                  </>
                )}

                {step === 2 && (
                  <>
                    <div className="p-4 bg-emerald-50 border border-emerald-200 rounded-xl">
                      <p className="text-sm text-gray-600 mb-1">Auto-detected category</p>
                      <p className="text-lg font-semibold text-emerald-800">{doctorCategory ? categoryLabelMap[doctorCategory] : "Not detected"}</p>
                    </div>
                    <div className="space-y-2">
                      <p className="text-sm font-medium text-gray-700">Available doctors in this category</p>
                      {categoryDoctors.length === 0 ? (
                        <div className="p-4 rounded-lg border border-amber-200 bg-amber-50 text-sm text-amber-800">
                          No doctors available in this category right now.
                        </div>
                      ) : (
                        <div className="grid gap-3">
                          {categoryDoctors.map((doctor) => {
                            const isSelected = selectedDoctorId === doctor.id;
                            return (
                              <button
                                key={doctor.id}
                                type="button"
                                onClick={() => handleSelectDoctor(doctor.id)}
                                className={`w-full rounded-xl border p-3 text-left transition ${
                                  isSelected
                                    ? "border-emerald-500 bg-emerald-50"
                                    : "border-gray-200 hover:border-emerald-300 hover:bg-emerald-50/40"
                                }`}
                              >
                                <p className="font-semibold text-gray-900">{doctor.name}</p>
                                <p className="text-sm text-gray-600">{doctor.experience} years • {doctor.clinic}</p>
                              </button>
                            );
                          })}
                        </div>
                      )}
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Change category (if needed)</label>
                      <select
                        value={doctorCategory}
                        onChange={(e) => {
                          setDoctorCategory(e.target.value as DoctorCategory);
                          setSelectedDoctorId(null);
                          setAutoAssignedDoctorId(null);
                          setSelectedDate("");
                          setSelectedTime("");
                        }}
                        className="w-full p-3 border border-gray-200 rounded-lg focus:ring-2 focus:ring-emerald-500"
                      >
                        {Object.entries(categoryLabelMap).map(([value, label]) => (
                          <option key={value} value={value}>{label}</option>
                        ))}
                      </select>
                    </div>
                    <div className="flex gap-3">
                      <button type="button" onClick={() => setStep(1)} className="px-5 py-2 border rounded-lg">Back</button>
                      <button
                        type="button"
                        onClick={handleAutoAssignDoctor}
                        disabled={!doctorCategory || categoryDoctors.length === 0}
                        className="flex-1 py-2 bg-emerald-500 text-white rounded-lg disabled:opacity-50"
                      >
                        Assign Doctor
                      </button>
                      <button
                        type="button"
                        onClick={() => setStep(3)}
                        disabled={!selectedDoctorId}
                        className="flex-1 py-2 bg-gradient-to-r from-[#1F5C3F] to-emerald-700 text-white rounded-lg disabled:opacity-50"
                      >
                        Continue with Selected Doctor
                      </button>
                    </div>
                  </>
                )}

                {step === 3 && (
                  <>
                    <div className="p-4 rounded-xl border border-emerald-200 bg-emerald-50">
                      <p className="text-sm text-gray-600">Selected doctor</p>
                      <p className="text-lg font-semibold text-emerald-800">{selectedDoctor?.name || "No doctor selected"}</p>
                      {selectedDoctor && (
                        <p className="text-sm text-gray-600">{selectedDoctor.experience} years • {selectedDoctor.clinic}</p>
                      )}
                    </div>

                    <div className="space-y-4">
                      <div className="flex items-center justify-between">
                        <p className="text-sm font-medium text-gray-700">Pick a date from calendar</p>
                        <div className="flex items-center gap-2">
                          <button
                            type="button"
                            onClick={() =>
                              setCalendarMonth(
                                (prev) => new Date(prev.getFullYear(), prev.getMonth() - 1, 1),
                              )
                            }
                            className="px-3 py-1.5 border rounded-lg text-sm"
                          >
                            Prev
                          </button>
                          <p className="min-w-[140px] text-center text-sm font-semibold text-gray-800">
                            {calendarMonth.toLocaleDateString("en-US", {
                              month: "long",
                              year: "numeric",
                            })}
                          </p>
                          <button
                            type="button"
                            onClick={() =>
                              setCalendarMonth(
                                (prev) => new Date(prev.getFullYear(), prev.getMonth() + 1, 1),
                              )
                            }
                            className="px-3 py-1.5 border rounded-lg text-sm"
                          >
                            Next
                          </button>
                        </div>
                      </div>

                      <div className="grid grid-cols-7 gap-2 text-xs sm:text-sm">
                        {["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"].map((weekday) => (
                          <div key={weekday} className="text-center font-semibold text-gray-500">
                            {weekday}
                          </div>
                        ))}
                      </div>

                      <div className="grid grid-cols-7 gap-2">
                        {calendarCells.map((dateCell, index) => {
                          if (!dateCell) {
                            return <div key={`empty-${index}`} className="h-20 rounded-lg bg-gray-50" />;
                          }

                          const slots = getSlotsForDate(dateCell);
                          const selectable = isDateSelectable(dateCell);
                          const dateValue = toDateInputValue(dateCell);
                          const isSelected = selectedDate === dateValue;

                          return (
                            <button
                              key={dateValue}
                              type="button"
                              disabled={!selectable}
                              onClick={() => {
                                setSelectedDate(dateValue);
                                setSelectedTime("");
                              }}
                              className={`h-20 rounded-lg border p-2 text-left transition ${
                                isSelected
                                  ? "border-emerald-500 bg-emerald-100"
                                  : selectable
                                    ? "border-emerald-200 bg-emerald-50 hover:border-emerald-400"
                                    : "border-gray-200 bg-gray-50 text-gray-400"
                              }`}
                            >
                              <p className="text-xs font-semibold">{dateCell.getDate()}</p>
                              <p className="mt-1 text-[11px]">
                                {slots.length > 0 ? `${slots.length} slots` : "Unavailable"}
                              </p>
                            </button>
                          );
                        })}
                      </div>
                    </div>

                    {selectedDate && (
                      <div className="space-y-3">
                        <p className="text-sm text-gray-600">Available slots for {dayName}</p>
                        {availableSlots.length === 0 ? (
                          <div className="p-4 rounded-lg bg-amber-50 border border-amber-200 text-amber-700 text-sm">
                            No slots available on this date. Please pick another available day.
                          </div>
                        ) : (
                          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-2">
                            {availableSlots.map((slot) => (
                              <button
                                key={slot}
                                type="button"
                                onClick={() => setSelectedTime(slot)}
                                className={`py-2 rounded-lg border text-sm font-medium ${
                                  selectedTime === slot
                                    ? "bg-emerald-500 border-emerald-500 text-white"
                                    : "bg-emerald-50 border-emerald-200 text-emerald-800"
                                }`}
                              >
                                <Clock className="w-4 h-4 inline mr-1" />
                                {formatTimeLabel(slot)}
                              </button>
                            ))}
                          </div>
                        )}
                      </div>
                    )}

                    <div className="flex gap-3">
                      <button type="button" onClick={() => setStep(2)} className="px-5 py-2 border rounded-lg">Back</button>
                      <button
                        type="button"
                        onClick={() => setStep(4)}
                        disabled={!selectedDate || !selectedTime}
                        className="flex-1 py-2 bg-emerald-500 text-white rounded-lg disabled:opacity-50"
                      >
                        Continue to Assigning Doctor
                      </button>
                    </div>
                  </>
                )}

                {step === 4 && (
                  <>
                    <div className="p-4 rounded-xl bg-blue-50 border border-blue-200">
                      <p className="text-sm text-blue-800">
                        Doctor is assigned from your manual selection or smart assignment, based on severity and category.
                      </p>
                    </div>

                    {selectedDoctor ? (
                      <div className="p-5 rounded-xl border border-emerald-200 bg-emerald-50">
                        <h3 className="text-lg font-semibold text-emerald-800 mb-2">Assigned Doctor</h3>
                        <p className="font-semibold text-gray-900">{selectedDoctor.name}</p>
                        <p className="text-sm text-gray-700">{categoryLabelMap[selectedDoctor.department]} • {selectedDoctor.experience} years</p>
                        <p className="text-sm text-gray-600">{selectedDoctor.clinic}</p>
                        <div className="mt-3 text-sm text-gray-700 space-y-1">
                          <p><span className="font-medium">Date:</span> {selectedDate}</p>
                          <p><span className="font-medium">Time:</span> {formatTimeLabel(selectedTime)}</p>
                        </div>
                      </div>
                    ) : (
                      <div className="p-4 rounded-xl border border-amber-200 bg-amber-50 text-amber-800">
                        No doctor is available for the selected slot. Please go back and select another doctor/date.
                      </div>
                    )}

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Consultation mode *</label>
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                        <button type="button" onClick={() => setConsultationMode("clinic")} className={`py-2 border rounded-lg ${consultationMode === "clinic" ? "bg-emerald-500 text-white border-emerald-500" : "border-gray-200"}`}>
                          <MapPin className="w-4 h-4 inline mr-1" /> In-Clinic
                        </button>
                        <button type="button" onClick={() => setConsultationMode("video")} className={`py-2 border rounded-lg ${consultationMode === "video" ? "bg-emerald-500 text-white border-emerald-500" : "border-gray-200"}`}>
                          <Video className="w-4 h-4 inline mr-1" /> Video
                        </button>
                      </div>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Additional notes</label>
                      <textarea value={additionalNotes} onChange={(e) => setAdditionalNotes(e.target.value)} rows={3} className="w-full p-3 border border-gray-200 rounded-lg" />
                    </div>

                    <div className="flex gap-3">
                      <button type="button" onClick={() => setStep(3)} className="px-5 py-2 border rounded-lg">Back</button>
                      <button
                        type="button"
                        onClick={handleConfirmBooking}
                        disabled={!selectedDoctor}
                        className="flex-1 py-2 bg-emerald-500 text-white rounded-lg disabled:opacity-50"
                      >
                        Confirm Appointment
                      </button>
                    </div>
                  </>
                )}

                {step === 5 && confirmedBooking && (
                  <>
                    <div className="p-4 rounded-xl border border-green-200 bg-green-50">
                      <div className="flex items-center gap-2 text-green-700 font-semibold mb-2">
                        <CheckCircle className="w-5 h-5" /> Appointment Booked Successfully
                      </div>
                      <p className="text-sm text-gray-700">Booking ID: {confirmedBooking.bookingId}</p>
                    </div>

                    <div className="grid md:grid-cols-2 gap-4 text-sm">
                      <div className="p-4 border rounded-lg">
                        <p className="font-semibold mb-2">Appointment Details</p>
                        <p>Date: {confirmedBooking.selectedDate}</p>
                        <p>Time: {confirmedBooking.selectedTime}</p>
                        <p>Mode: {confirmedBooking.consultationMode === "video" ? "Video" : "In-Clinic"}</p>
                        <p>Category: {categoryLabelMap[confirmedBooking.doctorCategory]}</p>
                      </div>
                      <div className="p-4 border rounded-lg">
                        <p className="font-semibold mb-2">Assigned Doctor</p>
                        <p>{confirmedBooking.assignedDoctor.name}</p>
                        <p>{confirmedBooking.assignedDoctor.department}</p>
                        <p>{confirmedBooking.assignedDoctor.clinic}</p>
                      </div>
                    </div>

                    <div className="flex gap-3">
                      <button
                        type="button"
                        onClick={() => downloadAppointmentPdf(confirmedBooking)}
                        className="flex-1 py-3 bg-[#1F5C3F] text-white rounded-lg font-semibold"
                      >
                        <Download className="w-4 h-4 inline mr-1" /> Download PDF Copy
                      </button>
                      <button type="button" onClick={() => setStep(1)} className="px-5 py-3 border rounded-lg">
                        Book Another
                      </button>
                    </div>
                  </>
                )}
              </div>
            </div>
          </div>

          <div className="lg:col-span-1">
            <div className="bg-white rounded-2xl shadow-xl border border-gray-200 overflow-hidden lg:sticky lg:top-8">
              <div className="bg-gradient-to-r from-[#10B981] to-emerald-600 p-4 sm:p-6">
                <h2 className="text-xl font-bold text-white flex items-center space-x-2">
                  <Activity className="w-5 h-5" />
                  <span>My Appointments</span>
                </h2>
              </div>

              <div className="p-5 space-y-4 max-h-[640px] overflow-y-auto">
                {bookings.length === 0 ? (
                  <div className="text-center py-10 text-gray-500">
                    <FileText className="w-12 h-12 mx-auto mb-3 text-gray-300" />
                    No bookings yet.
                  </div>
                ) : (
                  bookings.map((booking) => (
                    <div key={booking.id} className="border border-gray-200 rounded-xl p-4">
                      <div className="flex justify-between gap-2">
                        <p className="font-semibold text-gray-900">{booking.patientName}</p>
                        <span className="text-xs px-2 py-1 rounded-full bg-emerald-100 text-emerald-800">{booking.status}</span>
                      </div>
                      <p className="text-xs text-gray-500 mb-2">{booking.bookingId}</p>

                      <div className="text-sm text-gray-700 space-y-1">
                        <p><Calendar className="w-3 h-3 inline mr-1" /> {booking.selectedDate}</p>
                        <p><Clock className="w-3 h-3 inline mr-1" /> {booking.selectedTime}</p>
                        <p><Stethoscope className="w-3 h-3 inline mr-1" /> {booking.assignedDoctor.name}</p>
                        <p><AlertCircle className="w-3 h-3 inline mr-1" /> {categoryLabelMap[booking.doctorCategory]}</p>
                        <p><Pill className="w-3 h-3 inline mr-1" /> {booking.currentMedications || "No medications shared"}</p>
                        <p>Allergies: {booking.allergies || "None specified"}</p>
                      </div>

                      <button
                        type="button"
                        onClick={() => downloadAppointmentPdf(booking)}
                        className="mt-3 w-full py-2 border border-emerald-200 text-emerald-700 rounded-lg text-sm font-medium hover:bg-emerald-50"
                      >
                        <Download className="w-4 h-4 inline mr-1" /> Download PDF
                      </button>
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default PatientAppointments;
