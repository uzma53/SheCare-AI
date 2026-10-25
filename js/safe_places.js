/**
 * SheCare AI / SurvivorCare AI - Safe Places Module Linker
 * Harmonized alias ensuring zero duplication or conflict with NearbyPlaces.
 */
if (typeof NearbyPlaces !== 'undefined') {
  window.SafePlaces = NearbyPlaces;
}
if (typeof AgencyReporting !== 'undefined') {
  window.SafePlacesReporting = AgencyReporting;
}
