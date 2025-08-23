# Done-on-Collide Feature: Status Report & Reading List

## Feature Overview
Implementation of collision-triggered episode termination when agents collide with specific objects in the Madrona Escape Room environment.

## Current Status: 🟡 Partially Implemented

### ✅ Completed Components

1. **Data Structure Support**
   - `done_on_collide` field added to `CompiledLevel` struct (types.hpp:155)
   - Field properly integrated into C API and Python bindings
   - Test coverage for the field in place

2. **Component System**
   - `TriggersEpisodeDone` component created (types.hpp:112-114)
   - Component registered in ECS system (sim.cpp:49)
   - Added to `PhysicsEntity` archetype (types.hpp:132)

3. **Entity Marking**
   - Level generation updated to mark entities (level_gen.cpp:154-165, 311, 420)
   - Entities are tagged based on `done_on_collide` flag from compiled level
   - Floor plane explicitly excluded from triggering

4. **System Architecture**
   - `agentCollisionSystem` created and integrated (sim.cpp:306-337)
   - System properly placed in task graph after physics (sim.cpp:435-442)
   - Runs before done tracking system for proper override capability

### ❌ Pending Components

1. **Collision Detection Implementation**
   - Actual collision detection logic not implemented
   - Waiting for physics system API updates
   - Current implementation is a documented placeholder

## Technical Blockers

### Primary Issue: Physics System API Limitations

The Madrona physics system currently doesn't provide accessible methods for querying collision data:

1. **ContactConstraint Access**
   - `ContactConstraint` is created during narrowphase but not queryable via ECS
   - No `forEach` method available on physics constraint queries
   - Constraints are temporary entities not exposed to game logic

2. **Missing Collision Events**
   - `CollisionEvent` structure exists but not populated/exported
   - No callback system for collision notifications
   - No way to subscribe to collision pairs

3. **API Requirements**
   Need one of:
   - Queryable ContactConstraint entities
   - Collision event callbacks
   - Access to narrowphase results
   - Spatial query with actual contact verification

## Reading List

### Essential Documentation

1. **📖 Collision System Architecture**
   - File: `docs/architecture/COLLISION_SYSTEM.md`
   - Sections: Contact Constraint Solver, Collision Handling Pipeline, Creating Collision Handlers
   - Key insight: System defines structures but doesn't expose them for game logic

2. **📖 Physics System Source**
   - File: `external/madrona/include/madrona/physics.hpp`
   - Lines: 55-61 (ContactConstraint definition)
   - Lines: 95-98 (CollisionEvent definition)
   - Status: Structures exist but not accessible

3. **📖 Physics Implementation**
   - Files: `external/madrona/src/physics/physics.cpp`
   - Lines: 319-326 (Component registration)
   - Note: Components registered but not exported for queries

### Implementation References

4. **📖 Current Implementation**
   - File: `src/sim.cpp`
   - Lines: 306-337 (agentCollisionSystem placeholder)
   - Lines: 435-442 (Task graph integration)

5. **📖 Component Definitions**
   - File: `src/types.hpp`
   - Lines: 109-114 (TriggersEpisodeDone component)
   - Line: 132 (PhysicsEntity archetype update)
   - Line: 155 (done_on_collide field)

6. **📖 Entity Setup**
   - File: `src/level_gen.cpp`
   - Lines: 154-165 (setupEntityPhysics with triggers)
   - Lines: 311, 420 (Passing done_on_collide flag)

### Related Systems

7. **📖 ECS Query System**
   - File: `external/madrona/include/madrona/query.hpp`
   - Understanding query limitations and capabilities

8. **📖 Task Graph System**
   - File: `src/sim.cpp::setupTasks()`
   - Lines: 427-442 (Physics to collision to done pipeline)

## Implementation Plan

### Phase 1: Physics System Enhancement (Required)
1. Modify Madrona physics to expose ContactConstraints
2. Add query support for collision data
3. OR implement collision event system

### Phase 2: Collision Detection (Blocked)
1. Replace placeholder in agentCollisionSystem
2. Query physics collision data
3. Check TriggersEpisodeDone component
4. Set done flag on collision

### Phase 3: Testing & Validation
1. Create test levels with collision scenarios
2. Verify collision detection accuracy
3. Performance testing with multiple worlds

## Alternative Approaches Considered

### ❌ Proximity-Based Detection (Removed)
- Implemented sphere-sphere distance checking
- Too inaccurate for actual collision detection
- Removed in favor of waiting for proper physics integration

### ❌ BVH Spatial Queries
- Could use broadphase BVH for proximity
- Still wouldn't give actual collision contacts
- Would duplicate physics work

### ✅ Wait for Physics API Update (Current)
- Cleanest solution
- Leverages existing collision detection
- No duplicate computation

## Code Locations Summary

```
src/types.hpp:109-114        - TriggersEpisodeDone component
src/types.hpp:132            - PhysicsEntity archetype
src/types.hpp:155            - done_on_collide field
src/sim.cpp:49               - Component registration
src/sim.cpp:306-337          - Collision system (placeholder)
src/sim.cpp:435-442          - Task graph integration
src/level_gen.cpp:154-165    - Entity physics setup
src/level_gen.cpp:191        - Floor plane setup
src/level_gen.cpp:311,420    - Level generation integration
```

## Next Steps

1. **Immediate**: Commit current infrastructure to feature branch
2. **Short-term**: Work with Madrona team on physics API enhancement
3. **Long-term**: Complete collision detection implementation once API available

## Branch Status

- Branch: `feature/done_on_collide`
- Build: ✅ Passing
- Tests: ✅ Passing (feature not active)
- Ready for: Commit and PR (as infrastructure preparation)

---

*Last Updated: 2024-01-23*
*Author: Claude Code Assistant*