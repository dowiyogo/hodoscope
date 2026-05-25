//----------------------------------------------------------------------------
// DetectorConstruction.cc
//
// Construye el hodoscopio NA64-mini.
//
// Convención de coordenadas (mirar desde +Z, "el haz cae en -Z"):
//
//                   +Z (hacia los cósmicos)
//                    |
//                    |
//   ┌───────── X-sup ───────────┐   z =  +6.0 mm
//   ┌───────── X-inf ───────────┐   z =  +3.0 mm     (offset +2 mm en X)
//
//          ↕  D = 5 mm  (separación entre ejes)
//
//   ┌───────── Y-sup ───────────┐   z =  -3.0 mm
//   ┌───────── Y-inf ───────────┐   z =  -6.0 mm     (offset +2 mm en Y)
//                    |
//                    +X →
//
// Las barras del PLANO X son largas en Y (75 mm) y están separadas en X.
//   → el plano X reconstruye la coordenada X del muón.
// Las barras del PLANO Y son largas en X (75 mm) y están separadas en Y.
//   → el plano Y reconstruye la coordenada Y del muón.
//
// SiPMs (volúmenes lógicos delgados, sin física óptica todavía):
//   - X-sup: en Y-  (extremo Y< de cada barra)
//   - X-inf: en Y+  (lado opuesto, según la spec del proyecto)
//   - Y-sup: en X-  (extremo X< de cada barra)
//   - Y-inf: en X+  (lado opuesto)
//
// Numeración de barras (índice global):
//   0..7   X-sup
//   8..15  X-inf   (i_local = índice - 8)
//   16..23 Y-sup
//   24..31 Y-inf
//
// El offset global del asamble se elige tal que el centro geométrico está
// en (0,0,0). En el sistema interno de cada subplano, la barra i tiene
// centro x_i = -((nbars-1)/2)*pitch + i*pitch  con pitch = ancho + gap.
// Para nbars=8, ancho=3, gap=1: pitch=4, x_i = -14 + 4*i mm.
//----------------------------------------------------------------------------

#include "DetectorConstruction.hh"
#include "DetectorMessenger.hh"

#include "G4Material.hh"
#include "G4NistManager.hh"
#include "G4Box.hh"
#include "G4LogicalVolume.hh"
#include "G4PVPlacement.hh"
#include "G4SystemOfUnits.hh"
#include "G4PhysicalConstants.hh"
#include "G4UserLimits.hh"
#include "G4SDManager.hh"
#include "G4VisAttributes.hh"
#include "G4Colour.hh"
#include "G4MaterialPropertiesTable.hh"

#include "ScintillatorSD.hh"
#include "SiPMSD.hh"
#include "G4RunManager.hh"
#include "G4RotationMatrix.hh"
#include "G4OpticalSurface.hh"
#include "G4LogicalSkinSurface.hh"
#include "G4LogicalBorderSurface.hh"

#include <algorithm>
#include <cctype>
#include <string>

namespace {

G4String toLowerCopy(const G4String& value)
{
  G4String lowered = value;
  std::transform(lowered.begin(), lowered.end(), lowered.begin(),
                 [](unsigned char c) { return static_cast<char>(std::tolower(c)); });
  return lowered;
}

HodoscopeVariantConfig makeVariantConfig(HodoscopeVariant variant)
{
  switch (variant) {
    case HodoscopeVariant::Hod2018_Vikuiti:
      return {
        "Hod2018_Vikuiti",
        "VikuitiESR",
        "thin_passive_layer_or_surface",
        0.165 * mm,
        0.050 * mm,
        "BC408 (implemented as EJ200-equivalent)",
        "S12572-100P",
        false
      };
    case HodoscopeVariant::Hod2019_TiO2:
    default:
      return {
        "Hod2019_TiO2",
        "TiO2OpticalEpoxyPaint",
        "optical_surface_only",
        0.0 * mm,
        0.0 * mm,
        "BC408 (implemented as EJ200-equivalent)",
        "S12572-100P",
        false
      };
  }
}

} // namespace

DetectorConstruction::DetectorConstruction()
: G4VUserDetectorConstruction(),
  fBarLength    (75.0 * mm),
  fBarWidth     ( 3.0 * mm),
  fBarThickness ( 1.0 * mm),
  fGap          ( 1.0 * mm),
  fSepZ         ( 2.0 * mm),
  fOffset       ( 2.0 * mm),
  fD            ( 5.0 * mm),
  fNbars        ( 8 ),
  fSiPMThickness( 0.5 * mm)
{
  fVariant = HodoscopeVariant::Hod2019_TiO2;
  fVariantConfig = makeVariantConfig(fVariant);
  fMessenger = new DetectorMessenger(this);
}

DetectorConstruction::~DetectorConstruction()
{
  delete fMessenger;
}

//----------------------------------------------------------------------------
void DetectorConstruction::DefineMaterials()
{
  if (fScint) return;   // materiales ya definidos en la primera llamada
  auto* nist = G4NistManager::Instance();

  // Aire: tomado del NIST.
  fAir = nist->FindOrBuildMaterial("G4_AIR");

  // EJ-200: PVT-based plastic scintillator.
  // Composición típica: H/C ratio = 5.17/4.69 (atómica)
  // Densidad nominal: 1.023 g/cm^3
  // Masa molar relativa: 5.17*1.008 + 4.69*12.011 = 5.211 + 56.332 = 61.543
  // Fracciones másicas: f_H ≈ 0.0847, f_C ≈ 0.9153
  G4double densityEJ200 = 1.023 * g/cm3;
  G4Element* elH = nist->FindOrBuildElement("H");
  G4Element* elC = nist->FindOrBuildElement("C");

  auto* ej200 = new G4Material("EJ200", densityEJ200, 2);
  ej200->AddElement(elH, 0.0847);   // FRACCIÓN MÁSICA (no atómica)
  ej200->AddElement(elC, 0.9153);
  fScint = ej200;

  // Propiedades ópticas (sólo se "encienden" si fEnableOptical=true via macro).
  // Definidas siempre para que el camino quede listo.
  const G4int nE = 4;
  G4double phE [nE] = { 2.38*eV, 2.70*eV, 2.92*eV, 3.10*eV }; // ~520, 460, 425, 400 nm
  G4double rind[nE] = { 1.58, 1.58, 1.58, 1.58 };
  G4double abs [nE] = { 3.8*m, 3.8*m, 3.8*m, 3.8*m };          // bulk attenuation length
  G4double scnt[nE] = { 0.05, 0.30, 1.00, 0.20 };              // emission spectrum aproximado de EJ-200

  auto* mptScint = new G4MaterialPropertiesTable();
  mptScint->AddProperty("RINDEX",      phE, rind, nE);
  mptScint->AddProperty("ABSLENGTH",   phE, abs , nE);
  mptScint->AddProperty("SCINTILLATIONCOMPONENT1", phE, scnt, nE);
  mptScint->AddConstProperty("SCINTILLATIONYIELD",      10000./MeV);
  mptScint->AddConstProperty("RESOLUTIONSCALE",         1.0);
  mptScint->AddConstProperty("SCINTILLATIONTIMECONSTANT1", 2.1*ns);
  mptScint->AddConstProperty("SCINTILLATIONYIELD1",     1.0);
  fScint->SetMaterialPropertiesTable(mptScint);
  fScint->GetIonisation()->SetBirksConstant(0.126*mm/MeV);

  G4cout << "[HODO] EJ-200 optical MPT: present" << G4endl;
  G4cout << "[HODO] EJ-200 RINDEX: present" << G4endl;
  G4cout << "[HODO] EJ-200 ABSLENGTH: present" << G4endl;
  G4cout << "[HODO] EJ-200 SCINTILLATIONCOMPONENT1: present" << G4endl;
  G4cout << "[HODO] EJ-200 SCINTILLATIONYIELD: present" << G4endl;
  G4cout << "[HODO] EJ-200 RESOLUTIONSCALE: present" << G4endl;
  G4cout << "[HODO] EJ-200 SCINTILLATIONTIMECONSTANT1: present" << G4endl;
  G4cout << "[HODO] EJ-200 YIELDRATIO: present" << G4endl;

  // Aire: necesita RINDEX para que el optical tracking funcione cuando se active.
  G4double rindAir[nE] = { 1.0003, 1.0003, 1.0003, 1.0003 };
  auto* mptAir = new G4MaterialPropertiesTable();
  mptAir->AddProperty("RINDEX", phE, rindAir, nE);
  fAir->SetMaterialPropertiesTable(mptAir);

  // Silicio para el "ladrillo" del SiPM (placeholder material, el SD es lo importante).
  fSiPMMat = nist->FindOrBuildMaterial("G4_Si");
  G4double rindSi[nE] = { 3.5, 3.5, 3.5, 3.5 };
  auto* mptSi = new G4MaterialPropertiesTable();
  mptSi->AddProperty("RINDEX", phE, rindSi, nE);
  fSiPMMat->SetMaterialPropertiesTable(mptSi);

  // ---------------------------------------------------------------------
  // TiO2 (rutilo puro). Pintura reflectante externa (~50-100 μm) tipo
  // Eljen EJ-510. Este material se mantiene definido aunque NO se construya
  // un volumen físico de TiO2 en esta iteración (se modela vía
  // G4OpticalSurface, ver DefineOpticalSurfaces). Queda listo para una
  // iteración futura donde se quiera evaluar el aporte al MS:
  //
  //   - 50 μm de TiO2 puro (ρ=4.06 g/cm³) en cada cara → ≲0.3 mrad de MS
  //     adicional para muones MIP a 4 GeV (sub-dominante vs ~11 mrad
  //     intrínseco por la separación D=5 mm).
  //
  // Notas:
  //   - La pintura real es TiO2 disperso en aglutinante polimérico
  //     (densidad efectiva ~1.5-2 g/cm³). Aquí usamos rutilo puro como
  //     cota superior.
  //   - El material no lleva propiedades ópticas: el modelado óptico se
  //     hace en la superficie del centellador (la luz no se propaga
  //     dentro del TiO2 en el modelo "groundfrontpainted").
  // ---------------------------------------------------------------------
  G4Element* elTi = nist->FindOrBuildElement("Ti");
  G4Element* elO  = nist->FindOrBuildElement("O");
  fTiO2 = new G4Material("TiO2_paint", 4.06*g/cm3, 2);
  fTiO2->AddElement(elTi, 1);
  fTiO2->AddElement(elO,  2);
}

//----------------------------------------------------------------------------
void DetectorConstruction::BuildSubplane(char axis, G4int layer,
                                         G4double zCenter, G4int copyOffset,
                                         G4LogicalVolume* parentLV)
{
  // pitch = ancho de barra + gap (centro a centro)
  const G4double pitch = fBarWidth + fGap;            // 4 mm
  const G4double half  = (fNbars - 1) * pitch / 2.;   // 14 mm para 8 barras
  const G4double dShift = (layer == 1) ? fOffset : 0.;

  // Tamaño de la barra (orientación canónica "X-bar": largo en Y, ancho en X,
  // espesor en Z). Para el plano Y NO se cambia el LV — se rota el placement
  // 90° alrededor de Z más abajo.
  //
  // BUG-FIX (iter 0.1): la versión anterior creaba un G4Box con orientación
  // distinta en función de 'axis' pero el LV se construía SOLO la primera vez
  // (guard `if (!fScintLV)`). Como BuildSubplane se llama primero con axis='X',
  // el LV quedaba con orientación X y se reutilizaba para el plano Y, donde
  // todas las 8 barras pasaban a solaparse en y=0 y la reconstrucción
  // angular en Y fallaba.

  if (!fScintLV) {
    G4Box* barSolid = new G4Box("Bar_solid",
                                fBarWidth*0.5,     // X = ancho     3 mm
                                fBarLength*0.5,    // Y = largo    75 mm
                                fBarThickness*0.5);// Z = espesor   1 mm
    fScintLV = new G4LogicalVolume(barSolid, fScint, "Scint_LV");
    // Color blanco semi-transparente: la barra está pintada con TiO2
    // (la pintura se modela como G4OpticalSurface, no como volumen físico).
    auto* scintVis = new G4VisAttributes(G4Colour(0.95, 0.95, 0.95, 0.7));
    scintVis->SetForceSolid(true);
    fScintLV->SetVisAttributes(scintVis);

    // User limits: max step en el centellador para muestreo correcto del dE/dx.
    fScintLV->SetUserLimits(new G4UserLimits(0.1*mm));
  }

  // Para el SiPM también un único LV reutilizado.
  // Orientación canónica: SiPM en el extremo +Y de la barra X-canónica.
  //   X = ancho de la barra      (3 mm)
  //   Y = profundidad del SiPM   (0.5 mm)  ← era fBarThickness, BUG
  //   Z = espesor de la barra    (1 mm)    ← era fSiPMThickness, BUG
  G4Box* sipmSolid = new G4Box("SiPM_solid",
                                fBarWidth*0.5,
                                fSiPMThickness*0.5,
                                fBarThickness*0.5);
  if (!fSiPMLV) {
    fSiPMLV = new G4LogicalVolume(sipmSolid, fSiPMMat, "SiPM_LV");
    auto* sipmVis = new G4VisAttributes(G4Colour(1.0, 0.2, 0.2, 0.9));
    sipmVis->SetForceSolid(true);
    fSiPMLV->SetVisAttributes(sipmVis);
  }

  // Rotación común para barra y SiPM cuando estamos en plano Y:
  // 90° alrededor de Z gira la orientación canónica (largo en Y) a
  // largo en X. Se aplica al placement, no al LV.
  G4RotationMatrix* rot = nullptr;
  if (axis == 'Y') {
    rot = new G4RotationMatrix();
    rot->rotateZ(90.*deg);
  }

  // Posicionar las nbars barras del subplano.
  for (G4int i = 0; i < fNbars; ++i) {
    G4double posAxis = -half + i*pitch + dShift;   // posición a lo largo del eje "axis"
    G4ThreeVector pos;
    if (axis == 'X') {
      pos = G4ThreeVector(posAxis, 0., zCenter);
    } else {
      pos = G4ThreeVector(0., posAxis, zCenter);
    }

    G4int copyNo = copyOffset + i;   // 0..31 globalmente

    auto* scintPV = new G4PVPlacement(rot, pos, fScintLV,
                                      "Scint_PV",  parentLV,
                                      false, copyNo, true);
    fScintPVs.push_back(scintPV);

    // SiPM acoplado a la barra. Convención de lado:
    //   X-sup, Y-sup → lado "izquierdo" (negativo en el eje del largo)
    //   X-inf, Y-inf → lado "derecho"  (positivo en el eje del largo)
    G4double signSide = (layer == 0) ? -1.0 : +1.0;
    G4double sipmSep  = fBarLength*0.5 + fSiPMThickness*0.5;
    if (!fUseImprovedOpticalCoupling) sipmSep += 0.05*mm;

    G4ThreeVector sipmPos;
    if (axis == 'X') {
      // barra larga en Y → SiPM en Y±
      // como el SiPM_LV tiene dimensiones (W/2, T/2, S/2) en (x,y,z),
      // y queremos su lado largo (W) alineado con el ancho de la barra (X)
      // y su lado corto (T) en Y, la geometría está bien sin rotación.
      sipmPos = G4ThreeVector(posAxis, signSide*sipmSep, zCenter);
    } else {
      // barra larga en X → SiPM en X±
      // necesitamos rotar el SiPM_LV 90° en Z para que el lado largo
      // (W) quede alineado con el ancho de la barra (Y) en este caso.
      sipmPos = G4ThreeVector(signSide*sipmSep, posAxis, zCenter);
    }

    G4RotationMatrix* sipmRot = rot;  // misma rotación que la barra
    auto* sipmPV = new G4PVPlacement(sipmRot, sipmPos, fSiPMLV,
                                     "SiPM_PV", parentLV,
                                     false, copyNo, true);
    fSiPMPVs.push_back(sipmPV);
  }
}

//----------------------------------------------------------------------------
G4VPhysicalVolume* DetectorConstruction::DefineVolumes()
{
  fScintPVs.clear();
  fSiPMPVs.clear();
  fAssemblyPV = nullptr;

  // ---- World ---------------------------------------------------------------
  G4double worldHalf = 50.*cm;
  auto* worldSolid = new G4Box("World", worldHalf, worldHalf, worldHalf);
  auto* worldLV    = new G4LogicalVolume(worldSolid, fAir, "World_LV");
  worldLV->SetVisAttributes(G4VisAttributes::GetInvisible());

  auto* worldPV = new G4PVPlacement(nullptr, G4ThreeVector(),
                                    worldLV, "World_PV",
                                    nullptr, false, 0, true);

  // ---- Asamble del hodoscopio (logical volume "contenedor", de aire) ------
  G4double assXY = 0.5*( (fNbars-1)*(fBarWidth+fGap) + fBarWidth + fOffset )
                   + 5.*mm + fSiPMThickness; // margen para SiPMs y aire
  G4double assXY_half = std::max(assXY, fBarLength*0.5 + 5.*mm);
  G4double assZ_half  = 10.*mm;

  auto* assSolid = new G4Box("Assembly", assXY_half, assXY_half, assZ_half);
  auto* assLV    = new G4LogicalVolume(assSolid, fAir, "Assembly_LV");
  assLV->SetVisAttributes(G4VisAttributes::GetInvisible());

  fAssemblyPV = new G4PVPlacement(nullptr, G4ThreeVector(),
                                  assLV, "Assembly_PV", worldLV,
                                  false, 0, true);

  // ---- Cálculo de las Z de los 4 subplanos --------------------------------
  // Top de la pila a cota +Ztot/2, bottom a -Ztot/2.
  // Distancias centro-a-centro:
  //   X_sup → X_inf : barThk + sepZ
  //   X_inf → Y_sup : barThk + D    (D es gap entre superficies)
  //   Y_sup → Y_inf : barThk + sepZ
  G4double dz_sup_inf = fBarThickness + fSepZ;
  G4double dz_X_Y     = fBarThickness + fD;

  G4double Z_X_sup = +(dz_sup_inf + dz_X_Y)/2.;
  G4double Z_X_inf = Z_X_sup - dz_sup_inf;
  G4double Z_Y_sup = Z_X_inf - dz_X_Y;
  G4double Z_Y_inf = Z_Y_sup - dz_sup_inf;

  G4cout << "[DetectorConstruction] Z centers (mm):"
         << "  X_sup=" << Z_X_sup/mm
         << "  X_inf=" << Z_X_inf/mm
         << "  Y_sup=" << Z_Y_sup/mm
         << "  Y_inf=" << Z_Y_inf/mm
         << " | D=" << fD/mm << " mm"
         << G4endl;

  // ---- Construir los 4 subplanos -----------------------------------------
  BuildSubplane('X', 0, Z_X_sup,  0, assLV);
  BuildSubplane('X', 1, Z_X_inf,  8, assLV);
  BuildSubplane('Y', 0, Z_Y_sup, 16, assLV);
  BuildSubplane('Y', 1, Z_Y_inf, 24, assLV);

  return worldPV;
}

//----------------------------------------------------------------------------
G4VPhysicalVolume* DetectorConstruction::Construct()
{
  DefineMaterials();
  auto* world = DefineVolumes();
  DefineOpticalSurfaces();   // pintura TiO2 (skin surface)
  PrintDetectorConfiguration();
  return world;
}

//----------------------------------------------------------------------------
// Modelado óptico de la pintura blanca de TiO2 sobre las barras.
//
// Se utiliza el modelo 'unified' con finish 'groundfrontpainted', que es
// el estándar Geant4 para pinturas reflectantes difusas delgadas.
//
// Comportamiento del modelo:
//   - Un fotón óptico que incide sobre la superficie del centellador desde
//     el lado del centellador puede:
//        * reflejarse difusamente (Lambertian) con prob = REFLECTIVITY,
//        * ser absorbido con prob = 1 - REFLECTIVITY.
//   - No hay transmisión: el fotón nunca se propaga dentro del material
//     TiO2. Por eso el material TiO2 definido en DefineMaterials no aparece
//     como volumen físico — el efecto óptico está en la superficie.
//
// Reflectividad usada (típica EJ-510, dependiente de longitud de onda):
//        2.38 eV (~520 nm)  -> 0.97
//        2.70 eV (~460 nm)  -> 0.96
//        2.92 eV (~425 nm)  -> 0.93   (pico de emisión EJ-200)
//        3.10 eV (~400 nm)  -> 0.85
//
// LIMITACIÓN ACTUAL (a corregir cuando se active G4OpticalPhysics):
//   La superficie pinta las 6 caras de la barra, incluyendo la cara que
//   acopla al SiPM. En la realidad esa cara está sin pintar (con grasa
//   óptica). Mientras la física óptica esté DESHABILITADA, las superficies
//   son inertes y esto NO afecta la simulación de muones MIP.
//   Cuando se active el transporte óptico, hay que:
//     (a) Reestructurar el SiPM como hijo del volumen de barra (sin gap
//         de aire), o
//     (b) Definir G4LogicalBorderSurface(bar_PV, sipm_PV) con finish
//         'polished' para sobreescribir la skin en esa cara.
//----------------------------------------------------------------------------
void DetectorConstruction::DefineOpticalSurfaces()
{
  if (!fScintLV) return;
  if (!fEnableOptical) {
    G4cout << "[DetectorConstruction] Optical surfaces skipped "
           << "(fEnableOptical=false)" << G4endl;
    return;
  }

  const G4int nE = 4;
  G4double phE [nE] = { 2.38*eV, 2.70*eV, 2.92*eV, 3.10*eV };
  G4double effi[nE] = { 0.0,     0.0,     0.0,     0.0     };

  auto* surf = new G4OpticalSurface("Reflector_surface");
  surf->SetModel(unified);

  auto* mpt = new G4MaterialPropertiesTable();
  G4double refl[nE] = { 0.97, 0.96, 0.93, 0.85 };

  auto setTiO2Reflectivity = [&]() {
    refl[0] = 0.97; refl[1] = 0.96; refl[2] = 0.93; refl[3] = 0.85;
  };
  auto setEffectiveTiO2EpoxyReflectivity = [&]() {
    setTiO2Reflectivity();
    const G4double scale = fTio2EpoxyEffectiveR425 / 0.93;
    for (G4int i = 0; i < nE; ++i) {
      refl[i] = std::min(0.999, refl[i] * scale);
    }
  };
  auto setESRReflectivity = [&]() {
    refl[0] = 0.990; refl[1] = 0.990; refl[2] = 0.985; refl[3] = 0.970;
  };
  auto setDiffuseSurface = [&]() {
    surf->SetType(dielectric_dielectric);
    surf->SetFinish(groundfrontpainted);
    surf->SetSigmaAlpha(0.10);
  };
  auto setSpecularSurface = [&]() {
    surf->SetType(dielectric_metal);
    surf->SetFinish(polishedfrontpainted);
    surf->SetSigmaAlpha(0.02);
  };

  if (fReflectorDebugMode != 0) {
    if (fReflectorDebugMode == 1) {
      setDiffuseSurface();
      setTiO2Reflectivity();
      G4cout << "[DetectorConstruction] Reflector debug mode 1: "
             << "TiO2 reflectivity with diffuse groundfrontpainted surface"
             << G4endl;
    } else if (fReflectorDebugMode == 2) {
      setDiffuseSurface();
      setESRReflectivity();
      G4cout << "[DetectorConstruction] Reflector debug mode 2: "
             << "ESR reflectivity with diffuse groundfrontpainted surface"
             << G4endl;
    } else if (fReflectorDebugMode == 3) {
      setSpecularSurface();
      setTiO2Reflectivity();
      G4cout << "[DetectorConstruction] Reflector debug mode 3: "
             << "TiO2 reflectivity with specular polishedfrontpainted surface"
             << G4endl;
    } else {
      setSpecularSurface();
      setESRReflectivity();
      G4cout << "[DetectorConstruction] Reflector debug mode 4: "
             << "ESR reflectivity with specular polishedfrontpainted surface"
             << G4endl;
    }
  } else if (fVariant == HodoscopeVariant::Hod2018_Vikuiti) {
    setSpecularSurface();
    setESRReflectivity();
    G4cout << "[DetectorConstruction] Optical surface: Vikuiti ESR "
           << "(specular, R>=0.985 around 425 nm)" << G4endl;
  } else if (fVariant == HodoscopeVariant::Hod2019_TiO2 &&
             fTio2EpoxyEffectiveR425 >= 0.0) {
    if (fTio2EpoxySurfaceMode == "specular") {
      setSpecularSurface();
    } else {
      setDiffuseSurface();
    }
    setEffectiveTiO2EpoxyReflectivity();
    G4cout << "[DetectorConstruction] Optical surface: TiO2+epoxy effective "
           << "override enabled, R425=" << fTio2EpoxyEffectiveR425
           << ", surface_mode=" << fTio2EpoxySurfaceMode << G4endl;
  } else {
    setDiffuseSurface();
    setTiO2Reflectivity();
    G4cout << "[DetectorConstruction] Optical surface: TiO2 paint "
           << "(Lambertian/diffuse, R=0.93 around 425 nm)" << G4endl;
  }

  G4cout << "[DetectorConstruction] Reflector final REFLECTIVITY:";
  for (G4int i = 0; i < nE; ++i) {
    G4cout << " (" << phE[i] / eV << " eV, " << refl[i] << ")";
  }
  G4cout << G4endl;

  mpt->AddProperty("REFLECTIVITY", phE, refl, nE);
  mpt->AddProperty("EFFICIENCY",   phE, effi, nE);

  surf->SetMaterialPropertiesTable(mpt);
  G4cout << "[DetectorConstruction] Reflector EFFICIENCY: 0 "
         << "(detection is handled by SiPMSD, not reflector PDE)" << G4endl;

  if (!fUseImprovedOpticalCoupling) {
    new G4LogicalSkinSurface("Scint_reflector_skin", fScintLV, surf);
    G4cout << "[DetectorConstruction] Legacy reflector skin applied to Scint_LV"
           << G4endl;
    return;
  }

  if (!fAssemblyPV || fScintPVs.size() != fSiPMPVs.size()) {
    G4cerr << "[DetectorConstruction] Improved optical coupling requested, "
           << "but scintillator/SiPM physical volume pairs are incomplete."
           << G4endl;
    return;
  }

  auto* sipmSurf = new G4OpticalSurface("SiPM_coupling_surface");
  sipmSurf->SetModel(unified);
  sipmSurf->SetType(dielectric_dielectric);
  sipmSurf->SetFinish(polished);

  for (std::size_t i = 0; i < fScintPVs.size(); ++i) {
    new G4LogicalBorderSurface("Scint_to_air_reflector_border",
                               fScintPVs[i], fAssemblyPV, surf);
    new G4LogicalBorderSurface("Scint_to_SiPM_coupling_border",
                               fScintPVs[i], fSiPMPVs[i], sipmSurf);
  }

  G4cout << "[DetectorConstruction] Improved optical coupling defined for "
         << fScintPVs.size()
         << " bars: reflector border to assembly air plus polished SiPM border"
         << G4endl;
}

//----------------------------------------------------------------------------
void DetectorConstruction::ConstructSDandField()
{
  // Tras ReinitializeGeometry() este método se llama en cada nuevo run.
  // Reutilizamos el SD existente si ya fue registrado; de lo contrario
  // lo creamos. Esto evita el WARNING "already exists" del G4SDManager
  // y garantiza que fHCID quede correctamente inicializado en todos los runs.
  auto* sdMan = G4SDManager::GetSDMpointer();

  auto* scintSD = dynamic_cast<ScintillatorSD*>(
      sdMan->FindSensitiveDetector("ScintSD", false));
  if (!scintSD) {
    scintSD = new ScintillatorSD("ScintSD", "ScintHC");
    sdMan->AddNewDetector(scintSD);
  }
  if (fScintLV) fScintLV->SetSensitiveDetector(scintSD);

  auto* sipmSD = dynamic_cast<SiPMSD*>(
      sdMan->FindSensitiveDetector("SiPMSD", false));
  if (!sipmSD) {
    sipmSD = new SiPMSD("SiPMSD", "SiPMHC");
    sdMan->AddNewDetector(sipmSD);
  }
  if (fSiPMLV) fSiPMLV->SetSensitiveDetector(sipmSD);
}

//----------------------------------------------------------------------------
void DetectorConstruction::SetPlaneSeparationD(G4double D)
{
  fD = D;
  // re-build geometry on next run start
  G4RunManager::GetRunManager()->ReinitializeGeometry();
}

void DetectorConstruction::SetDetectorVariant(HodoscopeVariant variant)
{
  fVariant = variant;
  fVariantConfig = makeVariantConfig(variant);
  G4cout << "[DetectorConstruction] Detector variant set to "
    << fVariantConfig.variantLabel << G4endl;
  G4RunManager::GetRunManager()->ReinitializeGeometry();
}

void DetectorConstruction::SetDetectorVariantByName(const G4String& variantName)
{
  const G4String normalized = toLowerCopy(variantName);

  if (normalized == "tio2" || normalized == "hod2019" ||
      normalized == "hod2019_tio2") {
    SetDetectorVariant(HodoscopeVariant::Hod2019_TiO2);
    return;
  }

  if (normalized == "vikuiti" || normalized == "hod2018" ||
      normalized == "hod2018_vikuiti") {
    SetDetectorVariant(HodoscopeVariant::Hod2018_Vikuiti);
    return;
  }

  G4cerr << "[DetectorConstruction] Invalid detector variant '"
    << variantName << "'. Valid options: Hod2019, TiO2, Hod2019_TiO2, "
    << "Hod2018, Vikuiti, Hod2018_Vikuiti." << G4endl;
}

void DetectorConstruction::SetEnableOpticalPhysics(G4bool b)
{
  fEnableOptical = b;
  G4cout << "[DetectorConstruction] Optical physics flag = "
         << (b ? "ON" : "OFF") << G4endl;
}

void DetectorConstruction::SetUseImprovedOpticalCoupling(G4bool b)
{
  fUseImprovedOpticalCoupling = b;
  fScintLV = nullptr;
  fSiPMLV = nullptr;
  fAssemblyPV = nullptr;
  fScintPVs.clear();
  fSiPMPVs.clear();
  G4cout << "[DetectorConstruction] Improved optical coupling flag = "
         << (b ? "ON" : "OFF") << G4endl;
  G4RunManager::GetRunManager()->ReinitializeGeometry();
}

void DetectorConstruction::SetReflectorDebugMode(G4int mode)
{
  if (mode < 0 || mode > 4) {
    G4cerr << "[DetectorConstruction] Invalid reflector debug mode "
           << mode << ". Valid modes are 0..4." << G4endl;
    return;
  }

  fReflectorDebugMode = mode;
  fScintLV = nullptr;
  fSiPMLV = nullptr;
  fAssemblyPV = nullptr;
  fScintPVs.clear();
  fSiPMPVs.clear();
  G4cout << "[DetectorConstruction] Reflector debug mode = "
         << fReflectorDebugMode << G4endl;
  G4RunManager::GetRunManager()->ReinitializeGeometry();
}

void DetectorConstruction::SetTio2EpoxyEffectiveR425(G4double r)
{
  if (r < 0.0) {
    fTio2EpoxyEffectiveR425 = -1.0;
  } else if (r <= 0.999) {
    fTio2EpoxyEffectiveR425 = r;
  } else {
    G4cerr << "[DetectorConstruction] Invalid TiO2+epoxy R425 " << r
           << ". Valid range is [-1 disabled] or 0..0.999." << G4endl;
    return;
  }

  fScintLV = nullptr;
  fSiPMLV = nullptr;
  fAssemblyPV = nullptr;
  fScintPVs.clear();
  fSiPMPVs.clear();
  G4cout << "[DetectorConstruction] TiO2+epoxy effective R425 = "
         << (fTio2EpoxyEffectiveR425 < 0.0 ? G4String("disabled")
                                           : G4String(std::to_string(fTio2EpoxyEffectiveR425)))
         << G4endl;
  G4RunManager::GetRunManager()->ReinitializeGeometry();
}

void DetectorConstruction::SetTio2EpoxySurfaceMode(const G4String& mode)
{
  const G4String normalized = toLowerCopy(mode);
  if (normalized != "default" && normalized != "diffuse" &&
      normalized != "specular") {
    G4cerr << "[DetectorConstruction] Invalid TiO2+epoxy surface mode '"
           << mode << "'. Valid modes are default, diffuse, specular."
           << G4endl;
    return;
  }

  fTio2EpoxySurfaceMode = normalized;
  fScintLV = nullptr;
  fSiPMLV = nullptr;
  fAssemblyPV = nullptr;
  fScintPVs.clear();
  fSiPMPVs.clear();
  G4cout << "[DetectorConstruction] TiO2+epoxy surface mode = "
         << fTio2EpoxySurfaceMode << G4endl;
  G4RunManager::GetRunManager()->ReinitializeGeometry();
}

void DetectorConstruction::PrintDetectorConfiguration() const
{
  G4cout << "[DetectorConstruction] Detector variant selected: "
    << fVariantConfig.variantLabel << G4endl;
  G4cout << "[DetectorConstruction] Scintillator material: "
    << fVariantConfig.scintillatorMaterial << G4endl;
  G4cout << "[DetectorConstruction] Reflector type: "
    << fVariantConfig.reflectorName << G4endl;
  G4cout << "[DetectorConstruction] Reflector thickness: "
    << fVariantConfig.reflectorThicknessMm / mm << " mm" << G4endl;
  G4cout << "[DetectorConstruction] Kapton thickness: "
    << fVariantConfig.kaptonThicknessMm / mm << " mm" << G4endl;
  G4cout << "[DetectorConstruction] Reflector model: "
    << fVariantConfig.reflectorModel << G4endl;
  G4cout << "[DetectorConstruction] Physical layer enabled: "
    << (fVariantConfig.physicalLayerEnabled ? "yes" : "no") << G4endl;
  G4cout << "[DetectorConstruction] MPPC model: "
    << fVariantConfig.mppcModel << G4endl;
  G4cout << "[DetectorConstruction] Optical photons: "
    << (fEnableOptical ? "enabled" : "disabled") << G4endl;
  G4cout << "[DetectorConstruction] Improved optical coupling: "
    << (fUseImprovedOpticalCoupling ? "enabled" : "disabled") << G4endl;
  G4cout << "[DetectorConstruction] Reflector debug mode: "
    << fReflectorDebugMode << G4endl;
  G4cout << "[DetectorConstruction] TiO2+epoxy effective R425: ";
  if (fTio2EpoxyEffectiveR425 < 0.0) G4cout << "disabled";
  else G4cout << fTio2EpoxyEffectiveR425;
  G4cout << G4endl;
  G4cout << "[DetectorConstruction] TiO2+epoxy surface mode: "
    << fTio2EpoxySurfaceMode << G4endl;
}
