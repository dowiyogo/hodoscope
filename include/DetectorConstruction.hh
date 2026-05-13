//----------------------------------------------------------------------------
// DetectorConstruction.hh
//
// Construye el hodoscopio NA64-mini:
//   - 4 subplanos (X_sup, X_inf, Y_sup, Y_inf), 8 barras de EJ-200 c/u
//   - Ofssets relativos: 2 mm entre subplanos paralelos, D = 5 mm entre ejes
//   - 32 SiPMs como volúmenes lógicos delgados acoplados a cada barra
//
// Notación (consistente con la spec del proyecto):
//   D       : separación entre el plano X y el plano Y       (default 5 mm)
//   gap     : aire entre barras paralelas dentro de un plano (1 mm)
//   sepZ    : separación vertical entre subplanos sup/inf    (2 mm)
//   offset  : desplazamiento del subplano inferior           (2 mm)
//   nbars   : número de barras por subplano                  (8)
//
// El asamble se centra en (0, 0, 0) del World. Coordenadas internas
// equivalentes a la spec original (esquina en 0) tras aplicar offset global.
//----------------------------------------------------------------------------

#ifndef HODOSCOPE_DETECTOR_CONSTRUCTION_HH
#define HODOSCOPE_DETECTOR_CONSTRUCTION_HH

#include "G4VUserDetectorConstruction.hh"
#include "globals.hh"

#include <vector>

class G4LogicalVolume;
class G4Material;
class G4VPhysicalVolume;
class DetectorMessenger;

enum class HodoscopeVariant {
  Hod2019_TiO2,
  Hod2018_Vikuiti
};

struct HodoscopeVariantConfig {
  G4String variantLabel;
  G4String reflectorName;
  G4String reflectorModel;
  G4double reflectorThicknessMm;
  G4double kaptonThicknessMm;
  G4String scintillatorMaterial;
  G4String mppcModel;
  G4bool   physicalLayerEnabled;
};

class DetectorConstruction : public G4VUserDetectorConstruction
{
public:
  DetectorConstruction();
  ~DetectorConstruction() override;

  G4VPhysicalVolume* Construct() override;
  void ConstructSDandField() override;

  // ---- Setters expuestos al messenger (control desde macros) -------------
  void SetPlaneSeparationD(G4double D);   // separación entre eje X e Y
  void SetEnableOpticalPhysics(G4bool b); // activa MaterialPropertiesTable
  void SetUseImprovedOpticalCoupling(G4bool b);
  void SetReflectorDebugMode(G4int mode);
  void SetDetectorVariant(HodoscopeVariant variant);
  void SetDetectorVariantByName(const G4String& variantName);

  // ---- Getters útiles para análisis --------------------------------------
  G4double GetPlaneSeparationD() const { return fD; }
  G4int    GetNBars()           const { return fNbars; }
  HodoscopeVariant GetDetectorVariant() const { return fVariant; }
  const HodoscopeVariantConfig& GetDetectorVariantConfig() const { return fVariantConfig; }
  G4bool IsOpticalEnabled() const { return fEnableOptical; }
  G4bool IsImprovedOpticalCouplingEnabled() const { return fUseImprovedOpticalCoupling; }
  G4int GetReflectorDebugMode() const { return fReflectorDebugMode; }

private:
  // --- pasos de construcción ----------------------------------------------
  void DefineMaterials();
  G4VPhysicalVolume* DefineVolumes();
  void DefineOpticalSurfaces();   // pintura TiO2 + (futuro) acoplamiento SiPM
  void PrintDetectorConfiguration() const;

  // --- helpers para construir los 4 subplanos -----------------------------
  // axis   : 'X' o 'Y'         (plano que mide la coordenada axis)
  // layer  : 0 = superior, 1 = inferior
  // zCenter: posición Z central del subplano dentro del asamble
  // copyOffset : índice de la primera barra en este subplano (0, 8, 16, 24)
  void BuildSubplane(char axis, G4int layer, G4double zCenter,
                     G4int copyOffset, G4LogicalVolume* parentLV);

  // --- materiales ---------------------------------------------------------
  G4Material* fAir       = nullptr;
  G4Material* fScint     = nullptr;  // EJ-200 (PVT-based)
  G4Material* fSiPMMat   = nullptr;  // silicio (placeholder)
  G4Material* fTiO2      = nullptr;  // pintura reflectante (rutilo puro)

  // --- parámetros geométricos (modificables desde macro) -------------------
  G4double fBarLength;    // 75 mm
  G4double fBarWidth;     // 3 mm
  G4double fBarThickness; // 1 mm
  G4double fGap;          // 1 mm  aire entre barras de un mismo subplano
  G4double fSepZ;         // 2 mm  entre subplano sup e inf
  G4double fOffset;       // 2 mm  shift del subplano inferior
  G4double fD;            // 5 mm  separación entre eje X y eje Y
  G4int    fNbars;        // 8

  G4double fSiPMThickness; // 0.5 mm (placeholder)

  // --- volúmenes lógicos para el SD ---------------------------------------
  G4LogicalVolume* fScintLV  = nullptr;
  G4LogicalVolume* fSiPMLV   = nullptr;
  G4VPhysicalVolume* fAssemblyPV = nullptr;
  std::vector<G4VPhysicalVolume*> fScintPVs;
  std::vector<G4VPhysicalVolume*> fSiPMPVs;

  HodoscopeVariant        fVariant = HodoscopeVariant::Hod2019_TiO2;
  HodoscopeVariantConfig  fVariantConfig;
  G4bool fEnableOptical = false;
  G4bool fUseImprovedOpticalCoupling = false;
  G4int fReflectorDebugMode = 0;

  DetectorMessenger* fMessenger = nullptr;
};

#endif
