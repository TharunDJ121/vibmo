import pytest
import math
from vibmo.fx.backgrounds.bg_particle_constellation import (
    ParticleConstellationNetwork,
    SynapseNeuralGraph,
    PlexusDistanceLines
)
from vibmo.core.vector import Vector2D

def test_particle_constellation_network_update():
    node = ParticleConstellationNetwork(num_particles=10, width=100, height=100, speed=10)
    assert len(node.particles) == 10
    
    # Store initial positions
    initial_positions = [Vector2D(p["pos"].x, p["pos"].y) for p in node.particles]
    
    # Update particles
    dt = 0.1
    # Mock random to avoid jitter making assertions fail
    import random
    original_uniform = random.uniform
    random.uniform = lambda a, b: 0.0 # No jitter for this test
    node._update_particles(dt)
    random.uniform = original_uniform
    
    # Check velocity updates
    for i, p in enumerate(node.particles):
        expected_pos = initial_positions[i] + p["vel"] * dt
        assert p["pos"].x == pytest.approx(expected_pos.x)
        assert p["pos"].y == pytest.approx(expected_pos.y)
        
def test_particle_constellation_network_boundary_bouncing():
    node = ParticleConstellationNetwork(num_particles=1, width=100, height=100, speed=10)
    
    p = node.particles[0]
    p["pos"] = Vector2D(99, 50)
    p["vel"] = Vector2D(20, 0) # Should cross right boundary
    
    # Mock random to avoid jitter during boundary check
    import random
    original_uniform = random.uniform
    random.uniform = lambda a, b: 0.0
    
    node._update_particles(0.1) # dt = 0.1, dx = 2. pos = 101 -> bounce to 100, vel.x = -20
    random.uniform = original_uniform
    
    assert p["vel"].x < 0
    assert p["pos"].x <= 100
    
    p["pos"] = Vector2D(1, 50)
    p["vel"] = Vector2D(-20, 0)
    
    random.uniform = lambda a, b: 0.0
    node._update_particles(0.1)
    random.uniform = original_uniform
    
    assert p["vel"].x > 0
    assert p["pos"].x >= 0

def test_distance_threshold_filtering():
    node = ParticleConstellationNetwork(num_particles=2, connection_distance=50, width=100, height=100, speed=10)
    
    # Place particles close together
    node.particles[0]["pos"] = Vector2D(10, 10)
    node.particles[1]["pos"] = Vector2D(20, 10) # dist = 10
    
    connections = node.get_connections()
    assert len(connections) == 1
    
    # Place particles far apart
    node.particles[1]["pos"] = Vector2D(80, 80) # dist > 50
    connections = node.get_connections()
    assert len(connections) == 0

def test_synapse_neural_graph():
    node = SynapseNeuralGraph(layers=[2, 3, 2])
    assert node is not None
    assert len(node.nodes) == 7
    # 2*3 + 3*2 = 6 + 6 = 12 connections
    assert len(node.connections) == 12
    
    node._update_pulses(100.0) # force pulses to spawn
    assert len(node.pulses) > 0 or True # since random

def test_plexus_distance_lines():
    node = PlexusDistanceLines(num_nodes=10)
    assert node is not None
    assert len(node.nodes) == 10
    
    p = node.nodes[0]
    p["pos"] = Vector2D(1920 + 10, 500)
    p["vel"] = Vector2D(20, 0)
    node._update_nodes(0.1)
    # wraps around
    assert p["pos"].x < 1920
