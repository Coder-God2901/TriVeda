import { useRef, useState } from "react";
import { useLocation } from "wouter";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Checkbox } from "@/components/ui/checkbox";
import { Textarea } from "@/components/ui/textarea";
import {
  Stethoscope,
  User,
  Award,
  MapPin,
  FileText,
  CheckCircle2,
  UploadCloud,
  ArrowRight,
  ArrowLeft,
  Briefcase,
} from "lucide-react";
import BrandLogo from "@/components/common/BrandLogo";

const qualificationsList = [
  "BAMS (Bachelor of Ayurvedic Medicine & Surgery)",
  "MD (Ayurveda)",
  "PhD (Ayurveda)",
  "Ayurvedic Doctor",
  "Ayurvedic Therapist",
  "Diploma in Panchakarma",
  "Diploma in Ayurvedic Pharmacy",
  "Other",
];

export default function DoctorRegistration({
  onNavigate,
}: {
  onNavigate?: (view: string) => void;
}) {
  const [, setLocation] = useLocation();
  const contentRef = useRef<HTMLDivElement>(null);

  const [form, setForm] = useState({
    name: "",
    qualifications: [] as string[],
    otherQualification: "",
    locality: "",
    experience: "",
    certificates: "",
    previousWork: "",
    extraInfo: "",
  });
  const [stepErrors, setStepErrors] = useState<Record<string, string>>({});
  const [showSuccess, setShowSuccess] = useState(false);
  const [currentStep, setCurrentStep] = useState(1);

  const totalSteps = 3;
  const steps = [
    { id: 1, title: "Profile" },
    { id: 2, title: "Practice Details" },
    { id: 3, title: "Experience" },
  ];

  const handleChange = (field: string, value: string) => {
    setForm((prev) => ({ ...prev, [field]: value }));
    setStepErrors((prev) => {
      if (!prev[field]) return prev;
      const updated = { ...prev };
      delete updated[field];
      return updated;
    });
  };

  const handleQualificationToggle = (q: string) => {
    setForm((prev) => ({
      ...prev,
      qualifications: prev.qualifications.includes(q)
        ? prev.qualifications.filter((item) => item !== q)
        : [...prev.qualifications, q],
    }));

    setStepErrors((prev) => {
      if (!prev.qualifications && !(q === "Other" && prev.otherQualification)) {
        return prev;
      }
      const updated = { ...prev };
      delete updated.qualifications;
      if (q !== "Other") delete updated.otherQualification;
      return updated;
    });
  };

  const validateCurrentStep = () => {
    const errors: Record<string, string> = {};

    if (currentStep === 1) {
      if (!form.name.trim()) errors.name = "Full name is required";
      if (form.qualifications.length === 0) {
        errors.qualifications = "Select at least one qualification";
      }
      if (
        form.qualifications.includes("Other") &&
        !form.otherQualification.trim()
      ) {
        errors.otherQualification = "Please specify your qualification";
      }
    }

    if (currentStep === 2) {
      const experienceYears = Number(form.experience);

      if (!form.locality.trim()) errors.locality = "Locality is required";
      if (!form.experience.trim() || Number.isNaN(experienceYears) || experienceYears < 0) {
        errors.experience = "Enter valid experience in years";
      }
      if (!form.certificates.trim()) {
        errors.certificates = "Certificate details are required";
      }
    }

    if (currentStep === 3) {
      if (!form.previousWork.trim()) {
        errors.previousWork = "Previous work details are required";
      }
    }

    setStepErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleNext = () => {
    if (!validateCurrentStep()) return;

    if (currentStep < totalSteps) {
      setCurrentStep((prev) => prev + 1);
      setTimeout(() => {
        contentRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
      }, 100);
      return;
    }

    setShowSuccess(true);
  };

  const navigateToLogin = () => {
    if (onNavigate) {
      onNavigate("login");
    } else {
      setLocation("/login/doctor");
    }
  };

  const handleBack = () => {
    if (currentStep > 1) {
      setCurrentStep((prev) => prev - 1);
      setTimeout(() => {
        contentRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
      }, 100);
      return;
    }

    navigateToLogin();
  };

  const renderStep = () => {
    switch (currentStep) {
      case 1:
        return (
          <div className="space-y-5 animate-fade-in">
            <h3 className="flex items-center gap-2 text-lg font-semibold text-foreground">
              <User className="h-5 w-5 text-primary" />
              Doctor Profile
            </h3>

            <div>
              <Label className="mb-1.5 flex items-center gap-2">
                <User className="h-4 w-4 text-muted-foreground" />
                Full Name *
              </Label>
              <Input
                value={form.name}
                onChange={(e) => handleChange("name", e.target.value)}
                placeholder="Enter your full name"
                data-testid="input-doctor-name"
              />
              {stepErrors.name && (
                <p className="mt-1 text-xs text-red-500">{stepErrors.name}</p>
              )}
            </div>

            <div>
              <Label className="mb-2 flex items-center gap-2">
                <Award className="h-4 w-4 text-muted-foreground" />
                Qualifications *
              </Label>
              <div className="grid grid-cols-1 gap-2 sm:grid-cols-2">
                {qualificationsList.map((qualification) => (
                  <label
                    key={qualification}
                    className={`flex cursor-pointer items-center gap-2 rounded-lg border px-3 py-2.5 transition-colors ${
                      form.qualifications.includes(qualification)
                        ? "border-primary/30 bg-primary/10"
                        : "border-border bg-background"
                    }`}
                  >
                    <Checkbox
                      checked={form.qualifications.includes(qualification)}
                      onCheckedChange={() => handleQualificationToggle(qualification)}
                    />
                    <span className="text-sm text-foreground">{qualification}</span>
                  </label>
                ))}
              </div>
              {stepErrors.qualifications && (
                <p className="mt-1 text-xs text-red-500">{stepErrors.qualifications}</p>
              )}
            </div>

            {form.qualifications.includes("Other") && (
              <div>
                <Label className="mb-1.5">Specify Qualification *</Label>
                <Input
                  value={form.otherQualification}
                  onChange={(e) => handleChange("otherQualification", e.target.value)}
                  placeholder="Enter qualification"
                  data-testid="input-doctor-other-qualification"
                />
                {stepErrors.otherQualification && (
                  <p className="mt-1 text-xs text-red-500">{stepErrors.otherQualification}</p>
                )}
              </div>
            )}
          </div>
        );

      case 2:
        return (
          <div className="space-y-5 animate-fade-in">
            <h3 className="flex items-center gap-2 text-lg font-semibold text-foreground">
              <MapPin className="h-5 w-5 text-primary" />
              Practice Details
            </h3>

            <div>
              <Label className="mb-1.5 flex items-center gap-2">
                <MapPin className="h-4 w-4 text-muted-foreground" />
                Locality *
              </Label>
              <Input
                value={form.locality}
                onChange={(e) => handleChange("locality", e.target.value)}
                placeholder="City, State"
                data-testid="input-doctor-locality"
              />
              {stepErrors.locality && (
                <p className="mt-1 text-xs text-red-500">{stepErrors.locality}</p>
              )}
            </div>

            <div>
              <Label className="mb-1.5 flex items-center gap-2">
                <Briefcase className="h-4 w-4 text-muted-foreground" />
                Years of Experience *
              </Label>
              <Input
                type="number"
                min="0"
                value={form.experience}
                onChange={(e) => handleChange("experience", e.target.value)}
                placeholder="e.g. 5"
                data-testid="input-doctor-experience"
              />
              {stepErrors.experience && (
                <p className="mt-1 text-xs text-red-500">{stepErrors.experience}</p>
              )}
            </div>

            <div>
              <Label className="mb-1.5 flex items-center gap-2">
                <UploadCloud className="h-4 w-4 text-muted-foreground" />
                Certificates *
              </Label>
              <Textarea
                value={form.certificates}
                onChange={(e) => handleChange("certificates", e.target.value)}
                placeholder="Provide certificate details or upload link"
                rows={3}
                data-testid="input-doctor-certificates"
              />
              {stepErrors.certificates && (
                <p className="mt-1 text-xs text-red-500">{stepErrors.certificates}</p>
              )}
            </div>
          </div>
        );

      case 3:
        return (
          <div className="space-y-5 animate-fade-in">
            <h3 className="flex items-center gap-2 text-lg font-semibold text-foreground">
              <FileText className="h-5 w-5 text-primary" />
              Professional Experience
            </h3>

            <div>
              <Label className="mb-1.5 flex items-center gap-2">
                <FileText className="h-4 w-4 text-muted-foreground" />
                Previous Work / Experience *
              </Label>
              <Textarea
                value={form.previousWork}
                onChange={(e) => handleChange("previousWork", e.target.value)}
                placeholder="Describe your previous work or clinical experience"
                rows={4}
                data-testid="input-doctor-previous-work"
              />
              {stepErrors.previousWork && (
                <p className="mt-1 text-xs text-red-500">{stepErrors.previousWork}</p>
              )}
            </div>

            <div>
              <Label className="mb-1.5 flex items-center gap-2">
                <Stethoscope className="h-4 w-4 text-muted-foreground" />
                Additional Information
              </Label>
              <Textarea
                value={form.extraInfo}
                onChange={(e) => handleChange("extraInfo", e.target.value)}
                placeholder="Any additional details you'd like to share (optional)"
                rows={3}
                data-testid="input-doctor-extra-info"
              />
            </div>

            <div className="rounded-lg border border-primary/20 bg-primary/5 p-4">
              <p className="text-sm text-muted-foreground">
                Review your details and submit. Our team will verify your information before account activation.
              </p>
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <div className="mx-auto w-full max-w-6xl px-4 py-8 sm:px-6 sm:py-10 lg:px-8 lg:py-12">
        <Card className="overflow-hidden border border-primary/10 bg-card shadow-lg">
          <div className="bg-gradient-to-r from-[#1F5C3F] to-[#10B981] px-6 py-7 text-white sm:px-8 sm:py-8">
            <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <BrandLogo
                  textClassName="text-2xl text-white"
                  iconClassName="h-10 w-10"
                />
                <p className="mt-2 text-sm font-medium text-white/85">
                  Join TrivedaCare as a trusted Ayurvedic doctor.
                </p>
              </div>
              <div className="inline-flex items-center gap-3 rounded-2xl bg-white/15 px-4 py-3 backdrop-blur-sm">
                <div className="rounded-full bg-white/20 p-2.5">
                  <Stethoscope className="h-5 w-5" />
                </div>
                <div>
                  <p className="text-xs uppercase tracking-wide text-white/80">
                    Registration Progress
                  </p>
                  <p className="text-base font-semibold">
                    Step {currentStep} of {totalSteps}
                  </p>
                </div>
              </div>
            </div>
          </div>

          <div className="grid lg:grid-cols-[280px,1fr]">
            <aside className="hidden border-r border-border/80 bg-muted/40 px-6 py-7 lg:block">
              <h3 className="text-sm font-semibold uppercase tracking-wide text-muted-foreground">
                Onboarding Steps
              </h3>
              <div className="mt-5 space-y-3">
                {steps.map((step) => {
                  const isActive = step.id === currentStep;
                  const isCompleted = step.id < currentStep;

                  return (
                    <div
                      key={step.id}
                      className={`flex items-center gap-3 rounded-xl border px-3 py-3 transition-colors ${
                        isActive
                          ? "border-primary/30 bg-primary/10"
                          : isCompleted
                            ? "border-emerald-300/60 bg-emerald-50/70"
                            : "border-border/70 bg-background/70"
                      }`}
                    >
                      <div
                        className={`flex h-7 w-7 items-center justify-center rounded-full text-xs font-semibold ${
                          isCompleted
                            ? "bg-emerald-600 text-white"
                            : isActive
                              ? "bg-primary text-primary-foreground"
                              : "bg-muted text-muted-foreground"
                        }`}
                      >
                        {isCompleted ? <CheckCircle2 className="h-4 w-4" /> : step.id}
                      </div>
                      <p className="text-sm font-semibold text-foreground">{step.title}</p>
                    </div>
                  );
                })}
              </div>
            </aside>

            <CardContent ref={contentRef} className="px-5 py-6 sm:px-8 sm:py-8">
              {showSuccess ? (
                <div className="flex min-h-[340px] flex-col items-center justify-center text-center animate-fade-in">
                  <CheckCircle2 className="mb-4 h-14 w-14 text-emerald-600" />
                  <h2 className="mb-2 text-2xl font-semibold text-emerald-700">
                    Registration Submitted
                  </h2>
                  <p className="mb-5 max-w-md text-base text-muted-foreground">
                    Thank you for registering with TrivedaCare. Our team will verify your profile and contact you soon.
                  </p>
                  <Button
                    onClick={navigateToLogin}
                    className="rounded-lg bg-primary font-semibold text-primary-foreground shadow-md transition-all duration-300 hover:opacity-90"
                    data-testid="button-doctor-back-login"
                  >
                    <ArrowLeft className="mr-2 h-4 w-4" /> Back to Login
                  </Button>
                </div>
              ) : (
                <>
                  {renderStep()}

                  <div className="mt-8 flex justify-between gap-3">
                    <Button
                      variant="outline"
                      onClick={handleBack}
                      className="flex items-center gap-2 rounded-lg border-primary/25 text-primary hover:bg-primary/5"
                      data-testid="button-doctor-back"
                    >
                      <ArrowLeft className="h-4 w-4" />
                      {currentStep === 1 ? "Back to Login" : "Back"}
                    </Button>

                    <Button
                      onClick={handleNext}
                      className="flex items-center gap-2 rounded-lg bg-primary font-semibold text-primary-foreground shadow-md transition-all duration-300 hover:opacity-90"
                      data-testid="button-doctor-next"
                    >
                      {currentStep === totalSteps ? (
                        <>
                          Submit Registration <CheckCircle2 className="h-4 w-4" />
                        </>
                      ) : (
                        <>
                          Next <ArrowRight className="h-4 w-4" />
                        </>
                      )}
                    </Button>
                  </div>
                </>
              )}
            </CardContent>
          </div>
        </Card>
      </div>
    </div>
  );
}
