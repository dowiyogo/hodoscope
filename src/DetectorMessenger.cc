//----------------------------------------------------------------------------
// DetectorMessenger.cc
//----------------------------------------------------------------------------
#include "DetectorMessenger.hh"
#include "DetectorConstruction.hh"

#include "G4UIdirectory.hh"
#include "G4UIcmdWithADoubleAndUnit.hh"
#include "G4UIcmdWithADouble.hh"
#include "G4UIcmdWithABool.hh"
#include "G4UIcmdWithAnInteger.hh"
#include "G4UIcmdWithAString.hh"

DetectorMessenger::DetectorMessenger(DetectorConstruction* det)
: G4UImessenger(), fDet(det),
  fDir(nullptr), fDirDet(nullptr), fCmdVariant(nullptr), fCmdD(nullptr),
  fCmdOptical(nullptr), fCmdImprovedOptical(nullptr), fCmdReflectorDebugMode(nullptr),
  fCmdTio2EpoxyEffectiveR425(nullptr), fCmdTio2EpoxySurfaceMode(nullptr)
{
  fDir = new G4UIdirectory("/hodoscope/");
  fDir->SetGuidance("Hodoscope simulation control");

  fDirDet = new G4UIdirectory("/hodoscope/det/");
  fDirDet->SetGuidance("Geometry parameters");

  fCmdVariant = new G4UIcmdWithAString("/hodoscope/setDetectorVariant", this);
  fCmdVariant->SetGuidance("Set the detector variant: Hod2019/TiO2 or Hod2018/Vikuiti.");
  fCmdVariant->SetParameterName("variant", false);
  fCmdVariant->AvailableForStates(G4State_PreInit, G4State_Idle);

  fCmdD = new G4UIcmdWithADoubleAndUnit("/hodoscope/det/setD", this);
  fCmdD->SetGuidance("Set plane separation D between X and Y planes.");
  fCmdD->SetParameterName("D", false);
  fCmdD->SetUnitCategory("Length");
  fCmdD->SetDefaultUnit("mm");
  fCmdD->SetRange("D>0.");
  fCmdD->AvailableForStates(G4State_PreInit, G4State_Idle);

  fCmdOptical = new G4UIcmdWithABool("/hodoscope/det/optical", this);
  fCmdOptical->SetGuidance("Enable optical photon transport (placeholder flag).");
  fCmdOptical->SetParameterName("flag", false);
  fCmdOptical->AvailableForStates(G4State_PreInit, G4State_Idle);

  fCmdImprovedOptical = new G4UIcmdWithABool("/hodoscope/det/improvedOptical", this);
  fCmdImprovedOptical->SetGuidance("Enable improved optical coupling surfaces for SiPM detection.");
  fCmdImprovedOptical->SetParameterName("flag", false);
  fCmdImprovedOptical->AvailableForStates(G4State_PreInit, G4State_Idle);

  fCmdReflectorDebugMode = new G4UIcmdWithAnInteger("/hodoscope/det/reflectorDebugMode", this);
  fCmdReflectorDebugMode->SetGuidance("Diagnostic reflector model override.");
  fCmdReflectorDebugMode->SetGuidance("0=physical variant, 1=TiO2 R diffuse, 2=ESR R diffuse, 3=TiO2 R specular, 4=ESR R specular.");
  fCmdReflectorDebugMode->SetParameterName("mode", false);
  fCmdReflectorDebugMode->SetDefaultValue(0);
  fCmdReflectorDebugMode->SetRange("mode>=0 && mode<=4");
  fCmdReflectorDebugMode->AvailableForStates(G4State_PreInit, G4State_Idle);

  fCmdTio2EpoxyEffectiveR425 =
      new G4UIcmdWithADouble("/hodoscope/det/tio2EpoxyEffectiveR425", this);
  fCmdTio2EpoxyEffectiveR425->SetGuidance(
      "Set effective TiO2+epoxy reflectivity near 425 nm for Hod2019 only.");
  fCmdTio2EpoxyEffectiveR425->SetGuidance(
      "Use a value in [0, 0.999]. Negative values disable the override.");
  fCmdTio2EpoxyEffectiveR425->SetParameterName("r425", false);
  fCmdTio2EpoxyEffectiveR425->SetDefaultValue(-1.0);
  fCmdTio2EpoxyEffectiveR425->AvailableForStates(G4State_PreInit, G4State_Idle);

  fCmdTio2EpoxySurfaceMode =
      new G4UIcmdWithAString("/hodoscope/det/tio2EpoxySurfaceMode", this);
  fCmdTio2EpoxySurfaceMode->SetGuidance(
      "Set TiO2+epoxy effective surface mode: default, diffuse, or specular.");
  fCmdTio2EpoxySurfaceMode->SetParameterName("mode", false);
  fCmdTio2EpoxySurfaceMode->SetDefaultValue("default");
  fCmdTio2EpoxySurfaceMode->AvailableForStates(G4State_PreInit, G4State_Idle);
}

DetectorMessenger::~DetectorMessenger()
{
  delete fCmdTio2EpoxySurfaceMode;
  delete fCmdTio2EpoxyEffectiveR425;
  delete fCmdVariant;
  delete fCmdReflectorDebugMode;
  delete fCmdImprovedOptical;
  delete fCmdOptical;
  delete fCmdD;
  delete fDirDet;
  delete fDir;
}

void DetectorMessenger::SetNewValue(G4UIcommand* cmd, G4String val)
{
  if (cmd == fCmdVariant) {
    fDet->SetDetectorVariantByName(val);
  } else if (cmd == fCmdD) {
    fDet->SetPlaneSeparationD(fCmdD->GetNewDoubleValue(val));
  } else if (cmd == fCmdOptical) {
    fDet->SetEnableOpticalPhysics(fCmdOptical->GetNewBoolValue(val));
  } else if (cmd == fCmdImprovedOptical) {
    fDet->SetUseImprovedOpticalCoupling(fCmdImprovedOptical->GetNewBoolValue(val));
  } else if (cmd == fCmdReflectorDebugMode) {
    fDet->SetReflectorDebugMode(fCmdReflectorDebugMode->GetNewIntValue(val));
  } else if (cmd == fCmdTio2EpoxyEffectiveR425) {
    fDet->SetTio2EpoxyEffectiveR425(fCmdTio2EpoxyEffectiveR425->GetNewDoubleValue(val));
  } else if (cmd == fCmdTio2EpoxySurfaceMode) {
    fDet->SetTio2EpoxySurfaceMode(val);
  }
}
