//----------------------------------------------------------------------------
// RunAction.hh
//
// Crea y administra un TTree ROOT con info por evento.
// Usa G4AnalysisManager (envuelve TFile/TTree de forma portable).
//
// Branches:
//   eventID                   int
//   prim_x, prim_y, prim_z    double  [mm]    posición inicial primario
//   prim_px, prim_py, prim_pz double          dirección unitaria primario
//   prim_E                    double  [MeV]   energía cinética primario
//   edep_bar[32]              double  [MeV]   energía depositada por barra
//   nph_sipm[32]              int             fotones detectados por SiPM
//   tfirst_bar[32]            double  [ns]    tiempo del primer hit en cada barra
//----------------------------------------------------------------------------
#ifndef HODOSCOPE_RUN_ACTION_HH
#define HODOSCOPE_RUN_ACTION_HH

#include "G4UserRunAction.hh"
#include "globals.hh"

class G4Run;

class RunAction : public G4UserRunAction
{
public:
  RunAction();
  ~RunAction() override;   // ahora hace Write() + CloseFile()

  void BeginOfRunAction(const G4Run* run) override;
  void EndOfRunAction  (const G4Run* run) override;

private:
  // Bandera: el archivo ROOT fue abierto al menos una vez.
  G4bool   fFileOpen        = false;
  // Nombre del archivo actualmente abierto (sin extensión .root).
  // Permite detectar cambios de /analysis/setFileName entre bloques de D.
  G4String fCurrentFileName = "";
};

#endif
