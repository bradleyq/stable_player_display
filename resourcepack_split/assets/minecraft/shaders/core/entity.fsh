#version 150

#moj_import <minecraft:fog.glsl>
#moj_import <minecraft:dynamictransforms.glsl>

#if defined(ALPHA_CUTOUT) && !defined(EMISSIVE) && !defined(NO_OVERLAY) && !defined(APPLY_TEXTURE_MATRIX)
#define MAYBE_PLAYERDISP 1
#endif

uniform sampler2D Sampler0;

in float sphericalVertexDistance;
in float cylindricalVertexDistance;
in vec4 vertexColor;
in vec4 lightMapColor;
in vec4 overlayColor;
in vec2 texCoord0;
#ifdef MAYBE_PLAYERDISP
in vec2 texCoord1;
in float part;

#define FADERANGE 12.0
#define FADEBIAS 8.0
#define MINALPHA 0.25

const mat4 bayer4 = mat4( 0.0 / 16.0,  8.0 / 16.0,  2.0 / 16.0, 10.0 / 16.0,
                         12.0 / 16.0,  4.0 / 16.0, 14.0 / 16.0,  6.0 / 16.0,
                          3.0 / 16.0, 11.0 / 16.0,  1.0 / 16.0,  9.0 / 16.0,
                         15.0 / 16.0,  7.0 / 16.0, 13.0 / 16.0,  5.0 / 16.0);
                         
#endif

out vec4 fragColor;

void main() {
    vec4 color = texture(Sampler0, texCoord0);
#ifdef ALPHA_CUTOUT
    if (color.a < ALPHA_CUTOUT) {
        discard;
    }
#endif
    color *= vertexColor * ColorModulator;
#ifndef NO_OVERLAY
    color.rgb = mix(overlayColor.rgb, color.rgb, overlayColor.a);
#endif
#ifndef EMISSIVE
    color *= lightMapColor;
#endif
    fragColor = apply_fog(color, sphericalVertexDistance, cylindricalVertexDistance, FogEnvironmentalStart, FogEnvironmentalEnd, FogRenderDistanceStart, FogRenderDistanceEnd, FogColor);

#ifdef MAYBE_PLAYERDISP
    if (part > 1.0 - 10e-6 && fragColor.a < 1.0) {
        fragColor.a = max(fragColor.a, MINALPHA);

        vec3 underCol = texture(Sampler0, texCoord1).rgb;
        vec3 trueMix = mix(underCol, fragColor.rgb, fragColor.a);
        float fade = mix(fragColor.a, 1.0, clamp((cylindricalVertexDistance - FADEBIAS) / (FADERANGE - FADEBIAS), 0.0, 1.0));

        fragColor = vec4((trueMix - (1 - fade) * underCol) / fade,  fade);
        if (fragColor.a < bayer4[int(gl_FragCoord.x) % 4][int(gl_FragCoord.y) % 4] + (0.5 / 16.0)) {
            discard;
        }
        else {
            fragColor.a = 1.0;
        }
    }
#endif
}
