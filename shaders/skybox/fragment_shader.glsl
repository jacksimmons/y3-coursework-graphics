#version 130

in vec3 fragment_texCoord;
out vec4 final_color;

uniform samplerCube sampler_cube;

void main(void)
{
	vec3 fragment_texCoord = fragment_texCoord;
	final_color = texture(sampler_cube, fragment_texCoord);
}
