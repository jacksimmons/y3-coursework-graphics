#version 130

in vec3 fragment_tex_coord;
out vec4 final_color;

uniform samplerCube sampler_cube;

void main(void)
{
	vec3 fragment_tex_coord = fragment_tex_coord;
	final_color = texture(sampler_cube, fragment_tex_coord);
}
