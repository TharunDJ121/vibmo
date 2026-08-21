import random
import math
from typing import List, Tuple, Dict, Any
from vibmo.scene.node import Node
from vibmo.core.vector import Vector2D
from vibmo.core.color import Color, colors

class ParticleConstellationNetwork(Node):
    def __init__(self, num_particles: int = 50, connection_distance: float = 150.0, speed: float = 20.0, width: float = 1920, height: float = 1080, **kwargs):
        super().__init__(**kwargs)
        self.num_particles = num_particles
        self.connection_distance = connection_distance
        self.speed = speed
        self.width = width
        self.height = height
        self.particles = []
        for _ in range(self.num_particles):
            pos = Vector2D(random.uniform(0, width), random.uniform(0, height))
            rx, ry = random.uniform(-1, 1), random.uniform(-1, 1)
            if rx == 0 and ry == 0:
                rx = 1
            vel = Vector2D(rx, ry).normalize() * speed
            self.particles.append({"pos": pos, "vel": vel, "radius": random.uniform(2, 5)})
            
        self.last_time = 0.0
        
    def _update_particles(self, dt: float):
        for p in self.particles:
            # Brownian motion simulation: add small random jitter to velocity
            jitter_x = random.uniform(-1.0, 1.0) * self.speed * 0.1
            jitter_y = random.uniform(-1.0, 1.0) * self.speed * 0.1
            
            new_vel = p["vel"] + Vector2D(jitter_x, jitter_y)
            if abs(new_vel.x) > 0.001 or abs(new_vel.y) > 0.001:
                p["vel"] = new_vel.normalize() * p["vel"].length
            
            p["pos"] += p["vel"] * dt
            
            # Boundary bouncing
            if p["pos"].x < 0:
                p["vel"] = Vector2D(abs(p["vel"].x), p["vel"].y)
                p["pos"] = Vector2D(max(0.0, min(float(self.width), p["pos"].x)), p["pos"].y)
            elif p["pos"].x > self.width:
                p["vel"] = Vector2D(-abs(p["vel"].x), p["vel"].y)
                p["pos"] = Vector2D(max(0.0, min(float(self.width), p["pos"].x)), p["pos"].y)
                
            if p["pos"].y < 0:
                p["vel"] = Vector2D(p["vel"].x, abs(p["vel"].y))
                p["pos"] = Vector2D(p["pos"].x, max(0.0, min(float(self.height), p["pos"].y)))
            elif p["pos"].y > self.height:
                p["vel"] = Vector2D(p["vel"].x, -abs(p["vel"].y))
                p["pos"] = Vector2D(p["pos"].x, max(0.0, min(float(self.height), p["pos"].y)))
                
    def get_connections(self) -> List[Tuple[Dict[str, Any], Dict[str, Any], float]]:
        connections = []
        for i, p1 in enumerate(self.particles):
            for j, p2 in enumerate(self.particles[i+1:]):
                dist = p1["pos"].distance_to(p2["pos"])
                if dist < self.connection_distance:
                    connections.append((p1, p2, dist))
        return connections
        
    def draw(self, ctx: Any, time: float = 0.0) -> None:
        dt = time - self.last_time
        if dt > 0:
            self._update_particles(dt)
        self.last_time = time
            
        connections = self.get_connections()
        
        for p1, p2, dist in connections:
            alpha = max(0, 1.0 - (dist / self.connection_distance))
            ctx.set_source_rgba(colors.CYAN.r, colors.CYAN.g, colors.CYAN.b, alpha * 0.5)
            ctx.set_line_width(1.0)
            ctx.move_to(p1["pos"].x, p1["pos"].y)
            ctx.line_to(p2["pos"].x, p2["pos"].y)
            ctx.stroke()
            
        for p in self.particles:
            ctx.set_source_rgba(colors.CYAN.r, colors.CYAN.g, colors.CYAN.b, 0.8)
            ctx.arc(p["pos"].x, p["pos"].y, p["radius"], 0, math.pi * 2)
            ctx.fill()


class SynapseNeuralGraph(Node):
    def __init__(self, layers: List[int] = [4, 6, 6, 4], width: float = 1920, height: float = 1080, **kwargs):
        super().__init__(**kwargs)
        self.layers = layers
        self.width = width
        self.height = height
        self.nodes = []
        self.connections = []
        self.pulses = []
        self.last_time = 0.0
        
        # Generate nodes
        layer_spacing = width / (len(layers) + 1)
        for i, num_nodes in enumerate(layers):
            x = layer_spacing * (i + 1)
            node_spacing = height / (num_nodes + 1)
            layer_nodes = []
            for j in range(num_nodes):
                y = node_spacing * (j + 1)
                layer_nodes.append({"pos": Vector2D(x, y), "radius": random.uniform(4, 8), "layer": i})
            self.nodes.extend(layer_nodes)
            
        # Generate connections
        for i in range(len(self.nodes)):
            for j in range(i + 1, len(self.nodes)):
                n1 = self.nodes[i]
                n2 = self.nodes[j]
                if n2["layer"] == n1["layer"] + 1:
                    self.connections.append((n1, n2))

    def _update_pulses(self, dt: float):
        # randomly spawn pulses
        if random.random() < dt * 5.0 and self.connections:
            conn = random.choice(self.connections)
            self.pulses.append({"conn": conn, "progress": 0.0, "speed": random.uniform(0.5, 1.5)})
            
        # update existing pulses
        for pulse in self.pulses:
            pulse["progress"] += pulse["speed"] * dt
            
        self.pulses = [p for p in self.pulses if p["progress"] < 1.0]

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        dt = time - self.last_time
        if dt > 0:
            self._update_pulses(dt)
        self.last_time = time
        
        # Draw connections
        ctx.set_source_rgba(colors.PURPLE.r, colors.PURPLE.g, colors.PURPLE.b, 0.3)
        ctx.set_line_width(1.0)
        for n1, n2 in self.connections:
            ctx.move_to(n1["pos"].x, n1["pos"].y)
            ctx.line_to(n2["pos"].x, n2["pos"].y)
            ctx.stroke()
            
        # Draw pulses
        for pulse in self.pulses:
            n1, n2 = pulse["conn"]
            prog = pulse["progress"]
            pos = n1["pos"] + (n2["pos"] - n1["pos"]) * prog
            
            # Glow effect
            ctx.set_source_rgba(colors.PINK.r, colors.PINK.g, colors.PINK.b, 1.0 - (abs(prog - 0.5) * 2))
            ctx.arc(pos.x, pos.y, 4, 0, math.pi * 2)
            ctx.fill()
            
        # Draw nodes
        for node in self.nodes:
            ctx.set_source_rgba(colors.INDIGO.r, colors.INDIGO.g, colors.INDIGO.b, 0.8)
            ctx.arc(node["pos"].x, node["pos"].y, node["radius"], 0, math.pi * 2)
            ctx.fill()


class PlexusDistanceLines(Node):
    def __init__(self, num_nodes: int = 40, width: float = 1920, height: float = 1080, max_dist: float = 200.0, speed: float = 10.0, **kwargs):
        super().__init__(**kwargs)
        self.num_nodes = num_nodes
        self.width = width
        self.height = height
        self.max_dist = max_dist
        self.speed = speed
        self.nodes = []
        for _ in range(num_nodes):
            pos = Vector2D(random.uniform(0, width), random.uniform(0, height))
            rx, ry = random.uniform(-1, 1), random.uniform(-1, 1)
            if rx == 0 and ry == 0:
                rx = 1
            vel = Vector2D(rx, ry).normalize() * speed
            self.nodes.append({"pos": pos, "vel": vel, "radius": random.uniform(3, 7)})
            
        self.last_time = 0.0
        
    def _update_nodes(self, dt: float):
        for n in self.nodes:
            n["pos"] += n["vel"] * dt
            
            # wrap around (instead of bounce)
            if n["pos"].x < 0: n["pos"].x += self.width
            if n["pos"].x > self.width: n["pos"].x -= self.width
            if n["pos"].y < 0: n["pos"].y += self.height
            if n["pos"].y > self.height: n["pos"].y -= self.height

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        dt = time - self.last_time
        if dt > 0:
            self._update_nodes(dt)
        self.last_time = time
        
        # draw distance attenuated lines
        for i in range(len(self.nodes)):
            for j in range(i + 1, len(self.nodes)):
                n1 = self.nodes[i]
                n2 = self.nodes[j]
                
                # Check actual distance and wrapped distance for smooth edges
                dist = n1["pos"].distance_to(n2["pos"])
                
                if dist < self.max_dist:
                    alpha = 1.0 - (dist / self.max_dist)
                    # Polyhedron node lines
                    ctx.set_source_rgba(colors.EMERALD.r, colors.EMERALD.g, colors.EMERALD.b, alpha * 0.6)
                    ctx.set_line_width(1.0 + alpha)
                    ctx.move_to(n1["pos"].x, n1["pos"].y)
                    ctx.line_to(n2["pos"].x, n2["pos"].y)
                    ctx.stroke()
                    
        # draw floating polyhedrons (represented as squares for simplicity here, or circles)
        # let's draw them as small squares or diamonds
        for n in self.nodes:
            ctx.set_source_rgba(colors.TEAL.r, colors.TEAL.g, colors.TEAL.b, 0.7)
            
            # draw diamond
            r = n["radius"]
            x, y = n["pos"].x, n["pos"].y
            ctx.move_to(x, y - r)
            ctx.line_to(x + r, y)
            ctx.line_to(x, y + r)
            ctx.line_to(x - r, y)
            ctx.close_path()
            ctx.fill()
