import struct
import sys

import pygame
import zengl
import zengl_extras

zengl_extras.init()

pygame.init()
pygame.display.set_mode((720, 720), flags=pygame.OPENGL | pygame.DOUBLEBUF, vsync=True)

ctx = zengl.context()

size = pygame.display.get_window_size()
image = ctx.image(size, 'rgba8unorm', samples=4)
depth = ctx.image(size, 'depth24plus', samples=4)
uniform_buffer = ctx.buffer(size=80, uniform=True)

pipeline = ctx.pipeline(
    vertex_shader='''
        #version 330 core

        layout (std140) uniform Common {
            mat4 camera_matrix;
            vec4 camera_position;
        };

        vec3 vertices[24] = vec3[](
            vec3(0.000000, 1.000000, -0.500000),
            vec3(0.000000, 1.000000, 0.500000),
            vec3(0.500000, 0.866025, -0.500000),
            vec3(0.500000, 0.866025, 0.500000),
            vec3(0.866025, 0.500000, -0.500000),
            vec3(0.866025, 0.500000, 0.500000),
            vec3(1.000000, -0.000000, -0.500000),
            vec3(1.000000, -0.000000, 0.500000),
            vec3(0.866025, -0.500000, -0.500000),
            vec3(0.866025, -0.500000, 0.500000),
            vec3(0.500000, -0.866025, -0.500000),
            vec3(0.500000, -0.866025, 0.500000),
            vec3(-0.000000, -1.000000, -0.500000),
            vec3(-0.000000, -1.000000, 0.500000),
            vec3(-0.500000, -0.866025, -0.500000),
            vec3(-0.500000, -0.866025, 0.500000),
            vec3(-0.866025, -0.500000, -0.500000),
            vec3(-0.866025, -0.500000, 0.500000),
            vec3(-1.000000, 0.000000, -0.500000),
            vec3(-1.000000, 0.000000, 0.500000),
            vec3(-0.866025, 0.500000, -0.500000),
            vec3(-0.866025, 0.500000, 0.500000),
            vec3(-0.500000, 0.866025, -0.500000),
            vec3(-0.500000, 0.866025, 0.500000)
        );

        vec3 normals[14] = vec3[](
            vec3(-0.0000, 1.0000, -0.0000),
            vec3(0.5000, 0.8660, -0.0000),
            vec3(0.8660, 0.5000, -0.0000),
            vec3(1.0000, -0.0000, -0.0000),
            vec3(0.8660, -0.5000, -0.0000),
            vec3(0.5000, -0.8660, -0.0000),
            vec3(-0.0000, -1.0000, -0.0000),
            vec3(-0.5000, -0.8660, -0.0000),
            vec3(-0.8660, -0.5000, -0.0000),
            vec3(-1.0000, -0.0000, -0.0000),
            vec3(-0.8660, 0.5000, -0.0000),
            vec3(-0.0000, -0.0000, 1.0000),
            vec3(-0.5000, 0.8660, -0.0000),
            vec3(-0.0000, -0.0000, -1.0000)
        );

        vec2 texcoords[50] = vec2[](
            vec2(1.000000, 0.500000),
            vec2(0.000000, 0.500000),
            vec2(0.750000, 0.490000),
            vec2(1.000000, 1.000000),
            vec2(0.250000, 0.490000),
            vec2(0.000000, 1.000000),
            vec2(0.916667, 0.500000),
            vec2(0.870000, 0.457846),
            vec2(0.916667, 1.000000),
            vec2(0.370000, 0.457846),
            vec2(0.833333, 0.500000),
            vec2(0.957846, 0.370000),
            vec2(0.833333, 1.000000),
            vec2(0.457846, 0.370000),
            vec2(0.750000, 0.500000),
            vec2(0.990000, 0.250000),
            vec2(0.750000, 1.000000),
            vec2(0.490000, 0.250000),
            vec2(0.666667, 0.500000),
            vec2(0.957846, 0.130000),
            vec2(0.666667, 1.000000),
            vec2(0.457846, 0.130000),
            vec2(0.583333, 0.500000),
            vec2(0.870000, 0.042154),
            vec2(0.583333, 1.000000),
            vec2(0.370000, 0.042154),
            vec2(0.500000, 0.500000),
            vec2(0.750000, 0.010000),
            vec2(0.500000, 1.000000),
            vec2(0.250000, 0.010000),
            vec2(0.416667, 0.500000),
            vec2(0.630000, 0.042154),
            vec2(0.416667, 1.000000),
            vec2(0.130000, 0.042154),
            vec2(0.333333, 0.500000),
            vec2(0.542154, 0.130000),
            vec2(0.333333, 1.000000),
            vec2(0.042154, 0.130000),
            vec2(0.250000, 0.500000),
            vec2(0.510000, 0.250000),
            vec2(0.250000, 1.000000),
            vec2(0.010000, 0.250000),
            vec2(0.166667, 0.500000),
            vec2(0.542154, 0.370000),
            vec2(0.042154, 0.370000),
            vec2(0.166667, 1.000000),
            vec2(0.083333, 0.500000),
            vec2(0.630000, 0.457846),
            vec2(0.130000, 0.457846),
            vec2(0.083333, 1.000000)
        );

        int vertex_indices[132] = int[](
            1, 2, 0, 3, 4, 2, 5, 6, 4, 7, 8, 6, 9, 10, 8, 11, 12, 10, 13, 14, 12, 15, 16, 14, 17, 18, 16, 19,
            20, 18, 21, 13, 5, 21, 22, 20, 23, 0, 22, 6, 14, 22, 1, 3, 2, 3, 5, 4, 5, 7, 6, 7, 9, 8, 9, 11, 10,
            11, 13, 12, 13, 15, 14, 15, 17, 16, 17, 19, 18, 19, 21, 20, 5, 3, 1, 1, 23, 21, 21, 19, 17, 17, 15,
            13, 13, 11, 9, 9, 7, 5, 5, 1, 21, 21, 17, 13, 13, 9, 5, 21, 23, 22, 23, 1, 0, 22, 0, 2, 2, 4, 6, 6,
            8, 10, 10, 12, 14, 14, 16, 18, 18, 20, 22, 22, 2, 6, 6, 10, 14, 14, 18, 22
        );

        int normal_indices[132] = int[](
            0, 1, 0, 1, 2, 1, 2, 3, 2, 3, 4, 3, 4, 5, 4, 5, 6, 5, 6, 7, 6, 7, 8, 7, 8, 9, 8, 9, 10, 9, 11, 11,
            11, 10, 12, 10, 12, 0, 12, 13, 13, 13, 0, 1, 1, 1, 2, 2, 2, 3, 3, 3, 4, 4, 4, 5, 5, 5, 6, 6, 6, 7,
            7, 7, 8, 8, 8, 9, 9, 9, 10, 10, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11,
            11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 10, 12, 12, 12, 0, 0, 13, 13, 13, 13, 13, 13, 13, 13, 13,
            13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13
        );

        int texcoord_indices[132] = int[](
            3, 6, 0, 8, 10, 6, 12, 14, 10, 16, 18, 14, 20, 22, 18, 24, 26, 22, 28, 30, 26, 32, 34, 30, 36, 38,
            34, 40, 42, 38, 44, 29, 13, 45, 46, 42, 49, 1, 46, 15, 31, 47, 3, 8, 6, 8, 12, 10, 12, 16, 14, 16,
            20, 18, 20, 24, 22, 24, 28, 26, 28, 32, 30, 32, 36, 34, 36, 40, 38, 40, 45, 42, 13, 9, 4, 4, 48,
            44, 44, 41, 37, 37, 33, 29, 29, 25, 21, 21, 17, 13, 13, 4, 44, 44, 37, 29, 29, 21, 13, 45, 49, 46,
            49, 5, 1, 47, 2, 7, 7, 11, 15, 15, 19, 23, 23, 27, 31, 31, 35, 39, 39, 43, 47, 47, 7, 15, 15, 23,
            31, 31, 39, 47
        );

        out vec3 v_vertex;
        out vec3 v_normal;
        out vec2 v_texcoord;

        void main() {
            v_vertex = vertices[vertex_indices[gl_VertexID]];
            v_normal = normals[normal_indices[gl_VertexID]];
            v_texcoord = texcoords[texcoord_indices[gl_VertexID]];
            gl_Position = camera_matrix * vec4(v_vertex, 1.0);
        }
    ''',
    fragment_shader='''
        #version 330 core

        in vec3 v_normal;

        layout (location = 0) out vec4 out_color;

        void main() {
            vec3 light_direction = vec3(0.48, 0.32, 0.81);
            float lum = dot(light_direction, normalize(v_normal)) * 0.7 + 0.3;
            out_color = vec4(lum, lum, lum, 1.0);
        }
    ''',
    layout=[
        {
            'name': 'Common',
            'binding': 0,
        },
    ],
    resources=[
        {
            'type': 'uniform_buffer',
            'binding': 0,
            'buffer': uniform_buffer,
        },
    ],
    framebuffer=[image, depth],
    topology='triangles',
    cull_face='back',
    vertex_count=132,
)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    now = pygame.time.get_ticks() / 1000.0

    ctx.new_frame()
    image.clear()
    depth.clear()
    camera_position = (4.0, 3.0, 2.0)
    camera = zengl.camera(camera_position, aspect=1.0, fov=45.0)
    uniform_buffer.write(struct.pack('64s3f4x', camera, *camera_position))
    pipeline.render()
    image.blit()
    ctx.end_frame()

    pygame.display.flip()
