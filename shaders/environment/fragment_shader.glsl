#version 130

in vec3 normal_view_space;
in vec3 position_view_space;
in vec3 fragment_tex_coord;
out vec4 final_color;

uniform float alpha;
uniform samplerCube sampler_cube;
uniform mat4 V_t;

void main(void)
{
    vec3 I = normalize(-position_view_space);
    vec3 R = (V_t * vec4(reflect(I, normalize(normal_view_space)), 1.0f)).xyz;
    
    vec4 color = vec4(texture(sampler_cube, R).rgb, alpha);
    final_color = color;
}
