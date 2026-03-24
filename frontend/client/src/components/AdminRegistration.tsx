import { useRef, useState } from "react";
import { useLocation } from "wouter";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  ArrowLeft,
  ArrowRight,
  Building2,
  CheckCircle2,
  FileText,
  Globe,
  Hospital,
  Mail,
  MapPin,
  Phone,
  Shield,
  User,
  UserCog,
} from "lucide-react";
import BrandLogo from "@/components/common/BrandLogo";

interface AdminRegistrationProps {
  onNavigate?: (view: string) => void;
}

interface AdminFormData {
  hospitalName: string;
  hospitalType: string;
  address: string;
  city: string;
  state: string;
  website: string;
  adminName: string;
  adminEmail: string;
  adminPhone: string;
  adminPassword: string;
  confirmPassword: string;
  licenseNumber: string;
  establishedYear: string;
  departments: string;
  notes: string;
}

export default function AdminRegistration({ onNavigate }: AdminRegistrationProps) {
  const [, setLocation] = useLocation();
  const contentRef = useRef<HTMLDivElement>(null);

  const [currentStep, setCurrentStep] = useState(1);
  const [showSuccess, setShowSuccess] = useState(false);
  const [stepErrors, setStepErrors] = useState<Record<string, string>>({});
  const [formData, setFormData] = useState<AdminFormData>({
    hospitalName: "",
    hospitalType: "",
    address: "",
    city: "",
    state: "",
    website: "",
    adminName: "",
    adminEmail: "",
    adminPhone: "",
    adminPassword: "",
    confirmPassword: "",
    licenseNumber: "",
    establishedYear: "",
    departments: "",
    notes: "",
  });

  const steps = [
    { id: 1, title: "Hospital Profile" },
    { id: 2, title: "Admin Account" },
    { id: 3, title: "Organization Details" },
  ];

  const totalSteps = steps.length;

  const navigateToAdminLogin = () => {
    if (onNavigate) {
      onNavigate("login");
      return;
    }

    setLocation("/login/admin");
  };

  const handleInputChange = (field: keyof AdminFormData, value: string) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
    setStepErrors((prev) => {
      if (!prev[field]) return prev;
      const updated = { ...prev };
      delete updated[field];
      return updated;
    });
  };

  const validateStep = () => {
    const errors: Record<string, string> = {};

    if (currentStep === 1) {
      if (!formData.hospitalName.trim()) errors.hospitalName = "Hospital name is required";
      if (!formData.hospitalType.trim()) errors.hospitalType = "Hospital type is required";
      if (!formData.address.trim()) errors.address = "Address is required";
      if (!formData.city.trim()) errors.city = "City is required";
      if (!formData.state.trim()) errors.state = "State is required";
    }

    if (currentStep === 2) {
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      const phoneDigits = formData.adminPhone.replace(/\D/g, "");

      if (!formData.adminName.trim()) errors.adminName = "Admin full name is required";
      if (!formData.adminEmail.trim()) {
        errors.adminEmail = "Admin email is required";
      } else if (!emailRegex.test(formData.adminEmail.trim())) {
        errors.adminEmail = "Enter a valid email address";
      }

      if (!formData.adminPhone.trim()) {
        errors.adminPhone = "Admin phone is required";
      } else if (phoneDigits.length < 10) {
        errors.adminPhone = "Phone number must have at least 10 digits";
      }

      if (!formData.adminPassword) {
        errors.adminPassword = "Password is required";
      } else if (formData.adminPassword.length < 8) {
        errors.adminPassword = "Password must be at least 8 characters";
      }

      if (!formData.confirmPassword) {
        errors.confirmPassword = "Confirm your password";
      } else if (formData.confirmPassword !== formData.adminPassword) {
        errors.confirmPassword = "Passwords do not match";
      }
    }

    if (currentStep === 3) {
      const year = Number(formData.establishedYear);
      const thisYear = new Date().getFullYear();

      if (!formData.licenseNumber.trim()) errors.licenseNumber = "License number is required";
      if (!formData.establishedYear.trim()) {
        errors.establishedYear = "Established year is required";
      } else if (Number.isNaN(year) || year < 1800 || year > thisYear) {
        errors.establishedYear = `Enter a valid year between 1800 and ${thisYear}`;
      }

      if (!formData.departments.trim()) {
        errors.departments = "Departments information is required";
      }
    }

    setStepErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleNext = () => {
    if (!validateStep()) return;

    if (currentStep < totalSteps) {
      setCurrentStep((prev) => prev + 1);
      setTimeout(() => {
        contentRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
      }, 100);
      return;
    }

    setShowSuccess(true);
  };

  const handleBack = () => {
    if (currentStep > 1) {
      setCurrentStep((prev) => prev - 1);
      setTimeout(() => {
        contentRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
      }, 100);
      return;
    }

    navigateToAdminLogin();
  };

  const renderStep = () => {
    switch (currentStep) {
      case 1:
        return (
          <div className="space-y-4 animate-fade-in">
            <h3 className="mb-4 flex items-center gap-2 text-lg font-semibold">
              <Hospital className="h-5 w-5 text-primary" /> Hospital Profile
            </h3>

            <div>
              <Label className="mb-1 flex items-center gap-1">
                <Building2 className="h-4 w-4 text-muted-foreground" /> Hospital Name *
              </Label>
              <Input
                value={formData.hospitalName}
                onChange={(e) => handleInputChange("hospitalName", e.target.value)}
                placeholder="Enter hospital or organization name"
                data-testid="input-admin-hospital-name"
              />
              {stepErrors.hospitalName && <p className="mt-1 text-xs text-red-500">{stepErrors.hospitalName}</p>}
            </div>

            <div>
              <Label className="mb-1 flex items-center gap-1">
                <Hospital className="h-4 w-4 text-muted-foreground" /> Hospital Type *
              </Label>
              <Input
                value={formData.hospitalType}
                onChange={(e) => handleInputChange("hospitalType", e.target.value)}
                placeholder="e.g. Multi-speciality, Ayurveda Clinic, Wellness Center"
                data-testid="input-admin-hospital-type"
              />
              {stepErrors.hospitalType && <p className="mt-1 text-xs text-red-500">{stepErrors.hospitalType}</p>}
            </div>

            <div>
              <Label className="mb-1 flex items-center gap-1">
                <MapPin className="h-4 w-4 text-muted-foreground" /> Address *
              </Label>
              <Textarea
                value={formData.address}
                onChange={(e) => handleInputChange("address", e.target.value)}
                placeholder="Street address"
                rows={2}
                data-testid="input-admin-address"
              />
              {stepErrors.address && <p className="mt-1 text-xs text-red-500">{stepErrors.address}</p>}
            </div>

            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <div>
                <Label className="mb-1">City *</Label>
                <Input
                  value={formData.city}
                  onChange={(e) => handleInputChange("city", e.target.value)}
                  placeholder="City"
                  data-testid="input-admin-city"
                />
                {stepErrors.city && <p className="mt-1 text-xs text-red-500">{stepErrors.city}</p>}
              </div>
              <div>
                <Label className="mb-1">State *</Label>
                <Input
                  value={formData.state}
                  onChange={(e) => handleInputChange("state", e.target.value)}
                  placeholder="State"
                  data-testid="input-admin-state"
                />
                {stepErrors.state && <p className="mt-1 text-xs text-red-500">{stepErrors.state}</p>}
              </div>
            </div>

            <div>
              <Label className="mb-1 flex items-center gap-1">
                <Globe className="h-4 w-4 text-muted-foreground" /> Website
              </Label>
              <Input
                value={formData.website}
                onChange={(e) => handleInputChange("website", e.target.value)}
                placeholder="https://your-hospital.com"
                data-testid="input-admin-website"
              />
            </div>
          </div>
        );

      case 2:
        return (
          <div className="space-y-4 animate-fade-in">
            <h3 className="mb-4 flex items-center gap-2 text-lg font-semibold">
              <UserCog className="h-5 w-5 text-primary" /> Admin Account
            </h3>

            <div>
              <Label className="mb-1 flex items-center gap-1">
                <User className="h-4 w-4 text-muted-foreground" /> Admin Full Name *
              </Label>
              <Input
                value={formData.adminName}
                onChange={(e) => handleInputChange("adminName", e.target.value)}
                placeholder="Enter full name"
                data-testid="input-admin-name"
              />
              {stepErrors.adminName && <p className="mt-1 text-xs text-red-500">{stepErrors.adminName}</p>}
            </div>

            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <div>
                <Label className="mb-1 flex items-center gap-1">
                  <Mail className="h-4 w-4 text-muted-foreground" /> Admin Email *
                </Label>
                <Input
                  type="email"
                  value={formData.adminEmail}
                  onChange={(e) => handleInputChange("adminEmail", e.target.value)}
                  placeholder="admin@hospital.com"
                  data-testid="input-admin-email"
                />
                {stepErrors.adminEmail && <p className="mt-1 text-xs text-red-500">{stepErrors.adminEmail}</p>}
              </div>

              <div>
                <Label className="mb-1 flex items-center gap-1">
                  <Phone className="h-4 w-4 text-muted-foreground" /> Admin Phone *
                </Label>
                <Input
                  value={formData.adminPhone}
                  onChange={(e) => handleInputChange("adminPhone", e.target.value)}
                  placeholder="+91 98765 43210"
                  data-testid="input-admin-phone"
                />
                {stepErrors.adminPhone && <p className="mt-1 text-xs text-red-500">{stepErrors.adminPhone}</p>}
              </div>
            </div>

            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <div>
                <Label className="mb-1 flex items-center gap-1">
                  <Shield className="h-4 w-4 text-muted-foreground" /> Password *
                </Label>
                <Input
                  type="password"
                  value={formData.adminPassword}
                  onChange={(e) => handleInputChange("adminPassword", e.target.value)}
                  placeholder="Minimum 8 characters"
                  data-testid="input-admin-password"
                />
                {stepErrors.adminPassword && <p className="mt-1 text-xs text-red-500">{stepErrors.adminPassword}</p>}
              </div>

              <div>
                <Label className="mb-1 flex items-center gap-1">
                  <Shield className="h-4 w-4 text-muted-foreground" /> Confirm Password *
                </Label>
                <Input
                  type="password"
                  value={formData.confirmPassword}
                  onChange={(e) => handleInputChange("confirmPassword", e.target.value)}
                  placeholder="Re-enter password"
                  data-testid="input-admin-confirm-password"
                />
                {stepErrors.confirmPassword && <p className="mt-1 text-xs text-red-500">{stepErrors.confirmPassword}</p>}
              </div>
            </div>
          </div>
        );

      case 3:
        return (
          <div className="space-y-4 animate-fade-in">
            <h3 className="mb-4 flex items-center gap-2 text-lg font-semibold">
              <FileText className="h-5 w-5 text-primary" /> Organization Details
            </h3>

            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <div>
                <Label className="mb-1">License Number *</Label>
                <Input
                  value={formData.licenseNumber}
                  onChange={(e) => handleInputChange("licenseNumber", e.target.value)}
                  placeholder="Hospital or organization license"
                  data-testid="input-admin-license"
                />
                {stepErrors.licenseNumber && <p className="mt-1 text-xs text-red-500">{stepErrors.licenseNumber}</p>}
              </div>

              <div>
                <Label className="mb-1">Established Year *</Label>
                <Input
                  type="number"
                  value={formData.establishedYear}
                  onChange={(e) => handleInputChange("establishedYear", e.target.value)}
                  placeholder="e.g. 2008"
                  data-testid="input-admin-year"
                />
                {stepErrors.establishedYear && <p className="mt-1 text-xs text-red-500">{stepErrors.establishedYear}</p>}
              </div>
            </div>

            <div>
              <Label className="mb-1">Departments / Services *</Label>
              <Textarea
                value={formData.departments}
                onChange={(e) => handleInputChange("departments", e.target.value)}
                placeholder="List major departments or services"
                rows={3}
                data-testid="input-admin-departments"
              />
              {stepErrors.departments && <p className="mt-1 text-xs text-red-500">{stepErrors.departments}</p>}
            </div>

            <div>
              <Label className="mb-1">Additional Notes</Label>
              <Textarea
                value={formData.notes}
                onChange={(e) => handleInputChange("notes", e.target.value)}
                placeholder="Any additional info for onboarding (optional)"
                rows={3}
                data-testid="input-admin-notes"
              />
            </div>

            <div className="rounded-lg border border-primary/20 bg-primary/5 p-4">
              <p className="text-sm text-muted-foreground">
                After submission, our team will verify your organization and send activation details to the admin email.
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
            <div className="flex flex-col gap-5 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <BrandLogo textClassName="text-2xl text-white" iconClassName="h-10 w-10" />
                <p className="mt-2 text-sm font-medium text-white/85">
                  Register your hospital or care center on TrivedaCare.
                </p>
              </div>

              <div className="inline-flex items-center gap-3 rounded-2xl bg-white/15 px-4 py-3 backdrop-blur-sm">
                <div className="rounded-full bg-white/20 p-2.5">
                  <Shield className="h-5 w-5" />
                </div>
                <div>
                  <p className="text-xs uppercase tracking-wide text-white/80">Registration Progress</p>
                  <p className="text-base font-semibold">Step {currentStep} of {totalSteps}</p>
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

              <div className="mt-6 rounded-xl border border-emerald-300/40 bg-emerald-50/70 p-4">
                <p className="text-sm font-medium text-emerald-900">
                  Keep official documents handy to speed up verification.
                </p>
              </div>
            </aside>

            <CardContent ref={contentRef} className="px-5 py-6 sm:px-8 sm:py-8">
              {showSuccess ? (
                <div className="flex min-h-[320px] flex-col items-center justify-center text-center animate-fade-in">
                  <CheckCircle2 className="mb-4 h-14 w-14 text-emerald-600" />
                  <h2 className="mb-2 text-2xl font-semibold text-emerald-700">Registration Submitted</h2>
                  <p className="mb-5 max-w-md text-base text-muted-foreground">
                    Thank you for registering your organization. We will review your details and reach out on your admin email.
                  </p>
                  <Button
                    onClick={navigateToAdminLogin}
                    className="rounded-lg bg-primary font-semibold text-primary-foreground shadow-md transition-all duration-300 hover:opacity-90"
                    data-testid="button-admin-back-login"
                  >
                    <ArrowLeft className="mr-2 h-4 w-4" /> Back to Admin Login
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
                      data-testid="button-admin-back"
                    >
                      <ArrowLeft className="h-4 w-4" />
                      {currentStep === 1 ? "Back to Login" : "Back"}
                    </Button>

                    <Button
                      onClick={handleNext}
                      className="flex items-center gap-2 rounded-lg bg-primary font-semibold text-primary-foreground shadow-md transition-all duration-300 hover:opacity-90"
                      data-testid="button-admin-next"
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
