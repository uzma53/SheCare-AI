/**
 * SurvivorCare AI / SheCare AI - Nearby Healthcare Module
 * 
 * Harmonized alias for NearbyPlaces engine.
 * Ensures single map initialization, preventing duplicate HTML IDs or conflicting event listeners.
 */
(function() {
  if (typeof NearbyPlaces !== 'undefined') {
    window.NearbyHealthcare = NearbyPlaces;
  }
})();
