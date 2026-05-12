//----------------------------------------------------------------------------
// DetectorMessenger.cc
//----------------------------------------------------------------------------
#include "DetectorMessenger.hh"
#include "DetectorConstruction.hh"

#include "G4UIdirectory.hh"
#include "G4UIcmdWithADoubleAndUnit.hh"
#include "G4UIcmdWithABool.hh"
#include "G4UIcmdWithAString.hh"

DetectorMessenger::DetectorMessenger(DetectorConstruction* det)
: G4UImessenger(), fDet(det),
  fDir(nullptr), fDirDet(nullptr), fCmdVariant(nullptr), fCmdD(nullptr), fCmdOptical(nullptr)
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
}

DetectorMessenger::~DetectorMessenger()
{
  delete fCmdVariant;
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
  }
}
