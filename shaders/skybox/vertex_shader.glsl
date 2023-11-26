#version 330 core

//=== in attributes are read from the vertex array, one row per instance of the shader
layout (location = 0) in vec3 position;

//=== out attributes are interpolated on the face, and passed on to the fragment shader
out vec3 fragment_tex_coord;

uniform mat4 PVM;

void main(void)
{
	gl_Position = PVM * vec4(position, 1);
	gl_Position.z = gl_Position.w * 0.999;
	fragment_tex_coord = -position;
}
