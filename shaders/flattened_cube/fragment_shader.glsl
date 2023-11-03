#version 130

in vec3 fragment_texCoord;	// the fragment texture coordinates (note vec3 for cube map)

out vec4 final_color; 		// the only output is the fragment colour

uniform samplerCube sampler_cube;	// the cube map texture

void main(void)
{
	// sample from the cube map texture
	final_color = texture(sampler_cube, fragment_texCoord);
}
