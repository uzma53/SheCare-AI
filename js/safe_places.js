/**
 * SurvivorCare AI / SheCare AI - Safe Places Module
 * 
 * Harmonized alias for NearbyPlaces engine.
 * Ensures single map initialization, preventing duplicate HTML IDs or conflicting event listeners.
 */
(function() {
  if (typeof NearbyPlaces !== 'undefined') {
    window.SafePlaces = NearbyPlaces;
  }
})();
