//----------------------------------------------------------------------------
// DetectorMessenger.hh
//
// Comandos UI para modificar parámetros de geometría desde macros.
//
// Comandos expuestos:
//   /hodoscope/det/setD <valor> <unit>  -> separación entre planos X y Y
//   /hodoscope/det/optical <true|false> -> habilita G4 optical physics
//   /hodoscope/det/improvedOptical <true|false> -> acoplamiento óptico SiPM
//----------------------------------------------------------------------------
#ifndef HODOSCOPE_DETECTOR_MESSENGER_HH
#define HODOSCOPE_DETECTOR_MESSENGER_HH

#include "G4UImessenger.hh"
#include "globals.hh"

class DetectorConstruction;
class G4UIdirectory;
class G4UIcmdWithADoubleAndUnit;
class G4UIcmdWithADouble;
class G4UIcmdWithABool;
class G4UIcmdWithAnInteger;
class G4UIcmdWithAString;

class DetectorMessenger : public G4UImessenger
{
public:
  explicit DetectorMessenger(DetectorConstruction* det);
  ~DetectorMessenger() override;

  void SetNewValue(G4UIcommand* cmd, G4String val) override;

private:
  DetectorConstruction*       fDet;
  G4UIdirectory*              fDir;
  G4UIdirectory*              fDirDet;
  G4UIcmdWithAString*         fCmdVariant;
  G4UIcmdWithADoubleAndUnit*  fCmdD;
  G4UIcmdWithABool*           fCmdOptical;
  G4UIcmdWithABool*           fCmdImprovedOptical;
  G4UIcmdWithAnInteger*       fCmdReflectorDebugMode;
  G4UIcmdWithADouble*         fCmdTio2EpoxyEffectiveR425;
  G4UIcmdWithAString*         fCmdTio2EpoxySurfaceMode;
};

#endif
