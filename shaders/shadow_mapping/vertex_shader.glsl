#version 330 core

//=== in attributes are read from the vertex array, one row per instance of the shader
layout (location = 0) in vec3 position;
layout (location = 1) in vec3 normal;
layout (location = 3) in vec2 tex_coord;

out vec3 fragment_pos;   // the position of the vertex in view coordinates
out vec3 fragment_normal;     // the normal of the vertex in view coordinates
out vec2 fragment_tex_coord;
out vec4 fragment_pos_lightPV;

uniform mat4 PVM;
uniform mat4 VM;
uniform mat4 VM_it;
uniform mat4 light_PV;


void main() {
	gl_Position = PVM * vec4(position, 1.0f);
    fragment_pos = vec3(VM * vec4(position, 1.0f));
    fragment_normal = vec3(VM_it * normalize(vec4(normal, 1.0f)));
    fragment_tex_coord = tex_coord;
    fragment_pos_lightPV = light_PV * vec4(fragment_pos, 1.0f);
}
