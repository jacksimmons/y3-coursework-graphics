#version 330 core

//=== in attributes are read from the vertex array, one row per instance of the shader
layout (location = 0) in vec3 position;
layout (location = 1) in vec3 tex_coord;

//=== out attributes are interpolated on the face, and passed on to the fragment shader
out vec3 fragment_tex_coord;

void main(void)
{
	gl_Position = vec4(position,1); // just display on the screen, no projection
	fragment_tex_coord = tex_coord;	// pass the texture coordinates on
}
