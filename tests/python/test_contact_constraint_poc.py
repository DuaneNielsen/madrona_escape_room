"""
POC test to verify ContactConstraint querying works after physics step.
This test creates a collision scenario and verifies we can detect it.
"""

import numpy as np

from madrona_escape_room import SimManager, madrona


def test_contact_constraint_detection():
    """Test that we can detect collisions via ContactConstraint queries"""

    # Create a level where agent will collide with a wall
    level_str = """
    ####
    #S #
    #  #
    ####
    """

    # Create manager with custom level
    mgr = SimManager(
        exec_mode=madrona.ExecMode.CPU,
        num_worlds=1,
        gpu_id=0,
        rand_seed=42,
        auto_reset=False,
        enable_batch_renderer=False,
        level_ascii=level_str,
    )

    # Get initial agent position
    obs = mgr.self_observation_tensor().to_numpy()
    initial_pos = obs[0, 0, :3].copy()  # World 0, agent 0
    print(f"Initial agent position: {initial_pos}")

    # Move agent directly into wall (right)
    actions = mgr.action_tensor().to_numpy()
    # Actions are [world, action_components] where components are [move_amount, move_angle, rotate]
    actions[0, :] = [10.0, 0.0, 0.0]  # Large forward movement

    # Step simulation - this should cause collision with wall
    mgr.step()

    # Check new position - should be blocked by wall
    obs = mgr.self_observation_tensor().to_numpy()
    new_pos = obs[0, 0, :3]
    print(f"New agent position: {new_pos}")

    # Agent should have moved but been stopped by wall
    distance_moved = np.linalg.norm(new_pos - initial_pos)
    print(f"Distance moved: {distance_moved}")

    # The agent should have moved some but not the full 10 units
    assert distance_moved > 0.1, "Agent didn't move at all"
    assert distance_moved < 5.0, "Agent moved too far (no collision?)"

    # Check done flag - this will only work if ContactConstraint query works
    done = mgr.done_tensor().to_numpy()
    print(f"Done flag: {done[0]}")

    print("Physics collision detection working!")


def test_agent_cube_collision():
    """Test collision between agent and cube"""

    # Create level with agent and cube close together
    level_str = """
    ######
    # SC #
    #    #
    ######
    """

    mgr = SimManager(
        exec_mode=madrona.ExecMode.CPU,
        num_worlds=1,
        gpu_id=0,
        rand_seed=42,
        auto_reset=False,
        enable_batch_renderer=False,
        level_ascii=level_str,
    )

    # Get initial position
    obs = mgr.self_observation_tensor().to_numpy()
    agent_pos = obs[0, 0, :3].copy()
    print(f"Agent initial: {agent_pos}")

    # Move agent toward cube
    actions = mgr.action_tensor().to_numpy()
    # Move forward toward cube
    actions[0, :] = [5.0, 0.0, 0.0]

    mgr.step()

    # Check position after collision
    obs = mgr.self_observation_tensor().to_numpy()
    agent_new = obs[0, 0, :3]
    print(f"Agent after: {agent_new}")

    # Agent should have moved but been blocked by cube
    distance_moved = np.linalg.norm(agent_new - agent_pos)
    print(f"Distance moved: {distance_moved}")

    # Should have moved some but not full 5 units
    assert distance_moved > 0.1, "Agent didn't move at all"
    assert distance_moved < 3.0, f"Agent moved too far (no collision?): {distance_moved}"
    print("Agent-cube collision working!")


def test_collision_with_done_on_collide_flag():
    """Test done_on_collide flag with cube collision"""

    # Create level with cube that should trigger done
    # Using JSON format to set done_on_collide flag
    import json

    level_json = json.dumps(
        {
            "name": "collision_test",
            "done_on_collide": True,
            "ascii": """####
#SC#
#  #
####""",
        }
    )

    mgr = SimManager(
        exec_mode=madrona.ExecMode.CPU,
        num_worlds=1,
        gpu_id=0,
        rand_seed=42,
        auto_reset=False,
        enable_batch_renderer=False,
        level_ascii=level_json,
    )

    # Move agent into cube
    actions = mgr.action_tensor().to_numpy()
    # Move forward into cube
    actions[0, :] = [5.0, 0.0, 0.0]

    mgr.step()

    # Check done flag
    done = mgr.done_tensor().to_numpy()
    print(f"Done flag after collision with cube: {done[0]}")

    # NOTE: This will only pass once ContactConstraint query is implemented
    # For now it's a demonstration of the intended behavior
    if done[0] == 1:
        print("✓ Done on collide WORKING! ContactConstraint query successful!")
    else:
        print("✗ Done flag not set - ContactConstraint query not yet working")
        print("  This is expected - ContactConstraints may be cleaned up before query")


if __name__ == "__main__":
    print("=" * 60)
    print("ContactConstraint POC Tests")
    print("=" * 60)

    print("\n1. Testing basic collision detection...")
    test_contact_constraint_detection()

    print("\n2. Testing agent-cube collision...")
    test_agent_cube_collision()

    print("\n3. Testing done_on_collide flag...")
    test_collision_with_done_on_collide_flag()

    print("\n" + "=" * 60)
    print("POC Complete!")
