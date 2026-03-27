import ActiveConsultationWizard, {
  type AssessmentAnswer,
} from "./ActiveConsultationWizard";
import VaidyaAssistBot from "./VaidyaAssistBot";

interface ActiveConsultationFlowProps {
  appointmentId?: string | null;
  patientName: string;
  prakritiScores?: {
    vata?: number;
    pitta?: number;
    kapha?: number;
  };
  patientProfileSummary?: {
    age?: number;
    gender?: string;
    prakriti?: string;
    priority?: string;
    email?: string;
    phone?: string;
    issues?: string[];
    compliance?: number;
  };
  patientAssessmentAnswers: AssessmentAnswer[];
  initialDiagnosis?: {
    finalPrakriti?: string;
    finalVikriti?: string;
    chiefComplaint?: string;
  };
  onFinalizeSuccess?: () => void;
}

export default function ActiveConsultationFlow({
  appointmentId,
  patientName,
  prakritiScores,
  patientProfileSummary,
  patientAssessmentAnswers,
  initialDiagnosis,
  onFinalizeSuccess,
}: ActiveConsultationFlowProps) {
  return (
    <>
      <ActiveConsultationWizard
        appointmentId={appointmentId}
        patientName={patientName}
        prakritiScores={prakritiScores}
        patientProfileSummary={patientProfileSummary}
        patientAssessmentAnswers={patientAssessmentAnswers}
        initialDiagnosis={initialDiagnosis}
        onFinalizeSuccess={onFinalizeSuccess}
      />
      <VaidyaAssistBot contextLabel={`${patientName} Consultation`} />
    </>
  );
}
