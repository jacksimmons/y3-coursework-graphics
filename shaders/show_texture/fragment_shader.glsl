#version 330 core

in vec2 fragment_tex_coord;	// the fragment texture coordinates

out vec4 final_color; 		// the only output is the fragment colour

uniform sampler2D sampler;	// the cube map texture

void main(void)
{
	// sample from the cube map texture
	final_color = texture(sampler, fragment_tex_coord);
}
