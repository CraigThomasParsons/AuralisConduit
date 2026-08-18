'use strict';

const test = require('node:test');
const assert = require('node:assert/strict');

global.chrome = undefined;
global.document = {};
const { findFirst, isVisible, isClickable, isUsableComposer } = require('../chrome_extension/content.js');

function element(overrides = {}) {
    return {
        isConnected: true,
        disabled: false,
        getAttribute: () => null,
        getBoundingClientRect: () => ({ width: 20, height: 10 }),
        ...overrides
    };
}

test('findFirst respects selector priority and skips unusable matches', () => {
    const hidden = element({ getBoundingClientRect: () => ({ width: 0, height: 0 }) });
    const enabled = element();
    const root = {
        querySelectorAll(selector) {
            if (selector === '#preferred') return [hidden];
            if (selector === '#fallback') return [enabled];
            return [];
        }
    };
    const match = findFirst(['#preferred', '#fallback'], isClickable, root);
    assert.equal(match.element, enabled);
    assert.equal(match.selector, '#fallback');
});

test('disabled and aria-disabled controls are rejected', () => {
    assert.equal(isClickable(element({ disabled: true })), false);
    assert.equal(isUsableComposer(element({ getAttribute: (name) => name === 'aria-disabled' ? 'true' : null })), false);
});

test('visible connected controls are accepted', () => {
    const control = element();
    assert.equal(isVisible(control), true);
    assert.equal(isClickable(control), true);
});
