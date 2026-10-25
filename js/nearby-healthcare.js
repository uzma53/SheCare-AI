/**
 * SheCare AI / SurvivorCare AI - Nearby Healthcare Module Linker
 * Harmonized alias ensuring zero duplication or conflict with NearbyPlaces.
 */
if (typeof NearbyPlaces !== 'undefined') {
  window.NearbyHealthcare = NearbyPlaces;
}
if (typeof AgencyReporting !== 'undefined') {
  window.NearbyHealthcareReporting = AgencyReporting;
}
