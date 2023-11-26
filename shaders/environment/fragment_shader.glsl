#version 130

in vec3 normal_view_space;
in vec3 position_view_space;
in vec3 fragment_tex_coord;
out vec4 final_color;

uniform samplerCube sampler_cube;
uniform mat4 V_t;

void main(void)
{
	vec3 normal_view_space_normalized = normalize(normal_view_space);
	vec3 reflected = reflect(normalize(-position_view_space), normal_view_space_normalized);

	//final_color = vec4(1.0f, 0.0f, 0.0f, 1.0f);
	final_color = texture(sampler_cube, normalize(V_t * vec4(reflected, 1.0f)).xyz);
	//final_color = texture(sampler_cube, normalize(reflected));


	//final_color = texture(sampler_cube, fragment_texCoord);
//	frag_data = texture(sampler_cube, vec3(1,0,0));
	//final_color = vec4( fragment_texCoord, 1.0f );
}
